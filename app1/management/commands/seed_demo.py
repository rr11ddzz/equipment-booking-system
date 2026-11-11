from django.core.management.base import BaseCommand
from django.db import transaction
from app1.models import DeviceType, CPU, GPU, RAM, Equipment


class Command(BaseCommand):
    help = 'Create three fictional catalogue items without users, credentials or reservations.'

    @transaction.atomic
    def handle(self, *args, **options):
        device_type, _ = DeviceType.objects.get_or_create(TypeName='Demo workstation')
        cpu, _ = CPU.objects.get_or_create(Brand='Example', Model='Quad Core', ClockSpeed=3.2, Cores=4)
        gpu, _ = GPU.objects.get_or_create(Brand='Example', Model='Graphics', VRAM=4)
        ram, _ = RAM.objects.get_or_create(Capacity=16, Type='DDR4', Speed=3200)
        created = 0
        for index, name in enumerate(['Design workstation', 'Development workstation', 'Lab workstation'], 1):
            serial = f'PORTFOLIO-DEMO-{index:03}'
            if not Equipment.objects.filter(DeviceSerial=serial).exists():
                Equipment.objects.create(DeviceSerial=serial, DeviceName=name, DeviceTypeID=device_type,
                                         CPUID=cpu, GPUID=gpu, RAMID=ram, Availability=True)
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} fictional equipment items. Existing equipment was unchanged.'))
