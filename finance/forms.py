from django import forms
from .models import Transaction,Budget
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'transaction_type',
            'category',
            'amount',
            'description',
            'date',
        ]
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError(
                "Amount must be greater than zero."
            )
        return amount
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['month', 'amount']
        widgets = {
            'month': forms.TextInput(
                attrs={'type': 'month'}
            ),
        }
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError(
                "Budget must be greater than zero."
            )
        return amount