from django import forms
from .models import ReturnRequest

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ['reason', 'image_proof', 'bank_name', 'bank_account_number', 'bank_account_name']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Jelaskan alasan retur secara detail...'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: BCA / Dana / GoPay'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan nomor rekening'}),
            'bank_account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama sesuai buku tabungan'}),
        }