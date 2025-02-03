from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('reviews', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='order_item',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='accounts.orderitem'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('user', 'order_item')},
        ),
    ] 