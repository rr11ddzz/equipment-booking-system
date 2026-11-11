from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import CustomUser, DeviceType, CPU, GPU, RAM, Equipment, Booking


class ReservationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = CustomUser.objects.create_user('owner', password='test-only-password', ApprovalStatus=True)
        cls.other = CustomUser.objects.create_user('other', password='test-only-password', ApprovalStatus=True)
        cls.equipment = Equipment.objects.create(
            DeviceName='Demo workstation', DeviceSerial='DEMO-001',
            DeviceTypeID=DeviceType.objects.create(TypeName='Workstation'),
            CPUID=CPU.objects.create(Brand='Demo', Model='CPU', ClockSpeed=3, Cores=4),
            GPUID=GPU.objects.create(Brand='Demo', Model='GPU', VRAM=4),
            RAMID=RAM.objects.create(Capacity=16, Type='DDR4', Speed=3200),
        )

    def setUp(self):
        self.client.force_login(self.owner)
        self.start = timezone.localdate() + timedelta(days=7)
        self.end = self.start + timedelta(days=2)
        self.reserve = reverse('initiate_reservation', args=[self.equipment.pk])
        self.data = {'booking_date': self.start.isoformat(), 'return_date': self.end.isoformat()}

    def booking(self, **kwargs):
        data = dict(user=self.owner, equipment=self.equipment, booking_date=self.start, return_date=self.end)
        data.update(kwargs)
        return Booking.objects.create(**data)

    def test_valid_reservation_belongs_to_signed_in_user(self):
        response = self.client.post(self.reserve, {**self.data, 'user': self.other.pk})
        self.assertRedirects(response, reverse('user_profile'))
        self.assertEqual(Booking.objects.get().user, self.owner)

    def test_invalid_dates_are_rejected_without_creation(self):
        for data in [{}, {'booking_date': 'not-a-date', 'return_date': self.end},
                     {'booking_date': self.start, 'return_date': self.start-timedelta(days=1)},
                     {'booking_date': timezone.localdate()-timedelta(days=1), 'return_date': self.end}]:
            with self.subTest(data=data):
                self.assertEqual(self.client.post(self.reserve, data).status_code, 400)
                self.assertFalse(Booking.objects.exists())

    def test_same_day_reservation_is_allowed(self):
        self.assertEqual(self.client.post(self.reserve, {'booking_date': self.start, 'return_date': self.start}).status_code, 302)

    def test_overlap_and_touching_dates_are_blocked(self):
        self.booking(user=self.other)
        for start, end in [(self.start, self.end), (self.start-timedelta(days=1), self.end+timedelta(days=1)), (self.end, self.end+timedelta(days=1))]:
            with self.subTest(start=start, end=end):
                self.assertEqual(self.client.post(self.reserve, {'booking_date': start, 'return_date': end}).status_code, 400)
        self.assertEqual(Booking.objects.count(), 1)

    def test_nonoverlapping_dates_are_allowed(self):
        self.booking(user=self.other)
        self.assertEqual(self.client.post(self.reserve, {'booking_date': self.end+timedelta(days=1), 'return_date': self.end+timedelta(days=2)}).status_code, 302)

    def test_cancelled_returned_and_rejected_records_do_not_block(self):
        for state in [{'status': 'Cancelled'}, {'status': 'Returned'}, {'admin_approval': 'Rejected'}]:
            with self.subTest(state=state):
                Booking.objects.all().delete()
                self.booking(**state)
                self.assertEqual(self.client.post(self.reserve, self.data).status_code, 302)

    def test_open_ended_active_booking_blocks_dates(self):
        self.booking(return_date=None)
        self.assertEqual(self.client.post(self.reserve, self.data).status_code, 400)

    def test_unavailable_equipment_is_rejected(self):
        Equipment.objects.filter(pk=self.equipment.pk).update(Availability=False)
        self.assertEqual(self.client.post(self.reserve, self.data).status_code, 400)
        self.assertFalse(Booking.objects.exists())

    def test_unapproved_account_cannot_reserve(self):
        self.owner.ApprovalStatus = False
        self.owner.save()
        self.assertEqual(self.client.post(self.reserve, self.data).status_code, 403)
        self.assertFalse(Booking.objects.exists())

    def test_anonymous_user_must_sign_in(self):
        self.client.logout()
        self.assertEqual(self.client.post(self.reserve, self.data).status_code, 302)
        self.assertFalse(Booking.objects.exists())

    def test_get_cannot_create_or_cancel(self):
        booking = self.booking()
        self.assertEqual(self.client.get(self.reserve).status_code, 405)
        self.assertEqual(self.client.get(reverse('cancel_reservation', args=[booking.pk])).status_code, 405)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'Pending')

    def test_other_user_cannot_cancel(self):
        booking = self.booking(user=self.other)
        self.assertEqual(self.client.post(reverse('cancel_reservation', args=[booking.pk])).status_code, 404)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'Pending')

    def test_owner_cancellation_preserves_record_and_frees_dates(self):
        booking = self.booking()
        self.assertEqual(self.client.post(reverse('cancel_reservation', args=[booking.pk])).status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'Cancelled')
        self.assertEqual(self.client.post(self.reserve, self.data).status_code, 302)

    def test_returned_booking_cannot_be_rewritten(self):
        booking = self.booking(status='Returned')
        self.client.post(reverse('cancel_reservation', args=[booking.pk]))
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'Returned')

    def test_profile_hides_other_users_bookings(self):
        mine, other = self.booking(), self.booking(user=self.other)
        response = self.client.get(reverse('user_profile'))
        self.assertEqual(list(response.context['booking']), [mine])
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_csrf_required_for_mutations(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        booking = self.booking()
        self.assertEqual(client.post(self.reserve, self.data).status_code, 403)
        self.assertEqual(client.post(reverse('cancel_reservation', args=[booking.pk])).status_code, 403)

    def test_missing_equipment_returns_404(self):
        self.assertEqual(self.client.get(reverse('booking_page', args=[999999])).status_code, 404)

    def test_unapproved_login_is_denied(self):
        self.client.logout()
        self.owner.ApprovalStatus = False
        self.owner.save()
        response = self.client.post(reverse('login'), {'username': 'owner', 'password': 'test-only-password'})
        self.assertContains(response, 'not approved')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_demo_seed_can_be_repeated_without_duplicate_equipment(self):
        from django.core.management import call_command
        from io import StringIO
        original_users = CustomUser.objects.count()
        call_command('seed_demo', stdout=StringIO())
        call_command('seed_demo', stdout=StringIO())
        self.assertEqual(Equipment.objects.filter(DeviceSerial__startswith='PORTFOLIO-DEMO-').count(), 3)
        self.assertEqual(CustomUser.objects.count(), original_users)
