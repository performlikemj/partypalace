from django import forms

class ProductBulkUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='CSV file containing product information'
    )
    images_zip = forms.FileField(
        label='Images ZIP File',
        help_text='ZIP file containing product images'
    )