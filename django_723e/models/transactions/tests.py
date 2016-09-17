# -*- coding: utf-8 -*-

from django.test import TransactionTestCase
from django.contrib.auth.models import User

from django_723e.models.accounts.models import Account
from django_723e.models.currency.models import Currency
from django_723e.models.categories.models import Category
from django_723e.models.transactions.models import AbstractTransaction, DebitsCredits, Change
import datetime

class AccountTest(TransactionTestCase):

    def setUp(self):
        """
            Create a set of data to access during tests
            user foo
            currency euro, chf, thb
            account user.foo.account
            categories category1, category2
        """
        self.user = User.objects.create()
        self.user.login = "foo"
        self.user.save()

        self.euro = Currency.objects.create(name="Euro", sign=u"\u20AC", space=True, after_amount=True)
        self.chf = Currency.objects.create(name="Franc suisse", sign="CHF")
        self.thb = Currency.objects.create(name=u"Bahts Thaïlandais", sign="BHT")
        self.usd = Currency.objects.create(name=u"US Dollars", sign="USD")
        self.account = Account.objects.create(user=self.user, name="User Account", currency=self.euro)
        self.cat1 = Category.objects.create(user=self.user, name="Category 1")
        self.cat2 = Category.objects.create(user=self.user, name="Category 2")

    def test_CategoriesMoveRight(self):
        """
            Create sub-categories and try to move them from one level up.
            Using MPTT to keep an organized structure
        """
        # Check is move_children_right properly moved children's category one level up.
        self.cat1_1 = Category.objects.create(user=self.user, name="Category 1.1", parent=self.cat1)
        self.cat1_2 = Category.objects.create(user=self.user, name="Category 1.2", parent=self.cat1)
        self.cat1.move_children_right()
        self.assertEqual(self.cat1.get_children().count(), 0)

        # Check if disabled function properly moved children's category one level up.
        self.cat1_1.parent = self.cat1
        self.cat1_1.save()
        self.cat1_2.parent = self.cat1
        self.cat1_2.save()
        self.cat1.disable()
        self.assertEqual(self.cat1.get_children().count(), 0)


    def test_CategoriesDelete(self):
        """
            Try to delete a Category.
            If it has transaction, it is just disable to keep trace,
            and if no transaction attched, it is delete.
        """
        trans1 = DebitsCredits.objects.create(
              account=self.account,
              currency=self.euro,
              name="Shopping",
              amount=1,
              category=self.cat1
        )
        self.cat1.delete()
        self.assertEqual(self.cat1.active, False)

        trans1.delete()
        self.assertEqual(self.cat1.transactions.all().count(), 0)

        self.cat1.delete()
        self.assertEqual(Category.objects.all().count(), 1)


    def test_CategoriesSum(self):
        """
            Create a serie of transaction and verify calculated data

            J-3    trans    49.3 €    Enable     cat1
            J-2    trans    20 €      Disable    cat1
        """
        # First transaction
        trans1 = DebitsCredits.objects.create(account=self.account,
                                            date=datetime.date.today() - datetime.timedelta(days=3),
                                            name="Shopping",
                                            amount=49.3,
                                            currency=self.euro,
                                            category=self.cat1)
        self.assertNotEqual(trans1, None)

        # Second transaction
        trans2 = DebitsCredits.objects.create(account=self.account,
                                            date=datetime.date.today() - datetime.timedelta(days=2),
                                            name="Shopping",
                                            amount=20,
                                            currency=self.euro,
                                            category=self.cat1)
        self.assertNotEqual(trans2, None)

        # Check if disabled transaction are used in sum
        self.assertEqual(self.cat1.sum_between(datetime.date.today(), datetime.date.today()-datetime.timedelta(days=3)), 69.3)

        # Check if disabled transaction are used in sum
        trans2.active = False
        trans2.save()
        self.assertEqual(self.cat1.sum_between(datetime.date.today(), datetime.date.today()-datetime.timedelta(days=3)), 49.3)


    def test_Change(self):
        """
            Test if Change object calculate well the exchange_rate
        """
        change = Change.objects.create(account=self.account,
                                       date=datetime.datetime.today() - datetime.timedelta(days=1),
                                       name="Withdraw",
                                       amount=120,
                                       currency=self.euro,
                                       new_amount=140,
                                       new_currency=self.chf)
        self.assertNotEqual(change, None)
        self.assertEqual(change.exchange_rate(), 1.1666666666666667)

        change2 = Change.objects.create(account=self.account,
                                       date=datetime.datetime.today() - datetime.timedelta(days=1),
                                       name="Withdraw",
                                       amount=130,
                                       currency=self.euro,
                                       new_amount=140,
                                       new_currency=self.chf)
        self.assertNotEqual(change2, None)
        self.assertEqual(change2.exchange_rate(), 1.0769230769230769)

    def test_Change_Transactions(self):
        """
            Test if editing change update transaction new_Amount
        """
        transaction1 = DebitsCredits.objects.create(account=self.account,
                                            date=datetime.datetime.today() - datetime.timedelta(days=20),
                                            name="Buy a 6 CHF item",
                                            amount=6,
                                            currency=self.chf)
        # After this point, transaction 1 Should have no reference Value
        transaction1 = DebitsCredits.objects.get(pk=transaction1.pk)
        self.assertEqual(transaction1.amount, 6)
        self.assertEqual(transaction1.reference_amount, None)

        # We define a change rate after the transaction 1
        # and check if there is still no reference_amount
        Change.objects.create(account=self.account,
                               date=datetime.datetime.today() + datetime.timedelta(days=30),
                               name="Withdraw",
                               amount=80,
                               currency=self.euro,
                               new_amount=60,
                               new_currency=self.chf)
        transaction1 = DebitsCredits.objects.get(pk=transaction1.pk)
        self.assertEqual(transaction1.amount, 6)
        self.assertEqual(transaction1.reference_amount, None)

        # We define a change rate BEFORE transaction 1
        # To check if trsnaction reference_amount has been edited
        Change.objects.create(account=self.account,
                               date=datetime.datetime.today() - datetime.timedelta(days=30),
                               name="Withdraw",
                               amount=80,
                               currency=self.euro,
                               new_amount=60,
                               new_currency=self.chf)

        transaction1 = DebitsCredits.objects.get(pk=transaction1.pk)
        self.assertEqual(transaction1.amount, 6)
        self.assertEqual(transaction1.reference_amount, 8)

        # We now create a transaction in THB.
        # App should not be able to define an exchange rate
        transaction2 = DebitsCredits.objects.create(account=self.account,
                                            date=datetime.datetime.today() - datetime.timedelta(days=2),
                                            name="Buy an item using Thai Baths",
                                            amount=60,
                                            currency=self.thb)
        transaction2 = DebitsCredits.objects.get(pk=transaction2.pk)
        self.assertEqual(transaction2.amount, 60)
        self.assertEqual(transaction2.reference_amount, None)

        # Now we had a change rate from CHF to THB
        # Should be able to define a EUR > THB exchange rate from
        # EUR > CHF > THB
        # In this case 80€ > 60 CHF > 120 THB so a 60 THB item should be 40€
        Change.objects.create(account=self.account,
                               date=datetime.datetime.today() - datetime.timedelta(days=28),
                               name="Withdraw",
                               amount=60,
                               currency=self.chf,
                               new_amount=120,
                               new_currency=self.thb)

        transaction2 = DebitsCredits.objects.get(pk=transaction2.pk)
        self.assertEqual(transaction2.amount, 60)
        self.assertEqual(transaction2.reference_amount, 40)

        # If I buy a new item using THB, I should have refernce_amount using Euro exchange rate
        transaction3 = DebitsCredits.objects.create(account=self.account,
                                            date=datetime.datetime.today() - datetime.timedelta(days=20),
                                            name="Buy a 6 CHF item",
                                            amount=600,
                                            currency=self.thb)
        transaction3 = DebitsCredits.objects.get(pk=transaction3.pk)
        self.assertEqual(transaction3.amount, 600)
        self.assertEqual(transaction3.reference_amount, 400)

        # Now we test with a fourth transaction, from THB to USD
        # We had a change rate from CHF to THB
        # Should be able to define a EUR > THB exchange rate from
        # EUR > CHF > THB > USD
        # In this case 80€ > 60 CHF > 120 THB > 240 USD so a 240 USD item should be 80
        Change.objects.create(account=self.account,
                               date=datetime.datetime.today() - datetime.timedelta(days=27),
                               name="Withdraw",
                               amount=120,
                               currency=self.thb,
                               new_amount=240,
                               new_currency=self.usd)
        transaction4 = DebitsCredits.objects.create(account=self.account,
                                            date=datetime.datetime.today() - datetime.timedelta(days=20),
                                            name="Buy a 240 USD item",
                                            amount=240,
                                            currency=self.usd)
        transaction4 = DebitsCredits.objects.get(pk=transaction4.pk)
        self.assertEqual(transaction4.amount, 240)
        self.assertEqual(transaction4.reference_amount, 80)

    def test_Edit_Change_Propagation(self):
        """
            We need to evaluate if editing a Change propagate well to all transactions
            80€ > 60 CHF > 120 THB > 240 USD so a 240 USD item should be 80
        """
        change1 = Change.objects.create(account=self.account,
                               date=datetime.datetime.today() - datetime.timedelta(days=30),
                               name="Withdraw",
                               amount=80,
                               currency=self.euro,
                               new_amount=60,
                               new_currency=self.chf)
        change2 = Change.objects.create(account=self.account,
                               date=datetime.datetime.today() - datetime.timedelta(days=28),
                               name="Withdraw",
                               amount=60,
                               currency=self.chf,
                               new_amount=120,
                               new_currency=self.thb)
        change3 = Change.objects.create(account=self.account,
                               date=datetime.datetime.today() - datetime.timedelta(days=27),
                               name="Withdraw",
                               amount=120,
                               currency=self.thb,
                               new_amount=240,
                               new_currency=self.usd)
        transaction = DebitsCredits.objects.create(account=self.account,
                                            date=datetime.datetime.today() - datetime.timedelta(days=20),
                                            name="Buy a 240 USD item",
                                            amount=240,
                                            currency=self.usd)
        transaction = DebitsCredits.objects.get(pk=transaction.pk)
        self.assertEqual(transaction.amount, 240)
        self.assertEqual(transaction.reference_amount, 80)

        # Now we change the mount of change 2
        change2 = Change.objects.get(pk=change2.pk)
        change2.new_amount = 240
        change2.save()
        # 80€ > 60 CHF > 240 THB > 240 USD so a 240 USD item should be 40
        transaction = DebitsCredits.objects.get(pk=transaction.pk)
        self.assertEqual(transaction.amount, 240)
        self.assertEqual(transaction.reference_amount, 40)

        # Now we change the amount of change 1
        change1 = Change.objects.get(pk=change1.pk)
        change1.new_amount = 120
        change1.save()
        # 80€ > 120 CHF > 240 THB > 240 USD so a 240 USD item should be 20
        transaction = DebitsCredits.objects.get(pk=transaction.pk)
        self.assertEqual(transaction.amount, 240)
        self.assertEqual(transaction.reference_amount, 20)

        # We create a second transaction before actually changing USD
        # transaction_rate will not be calculable
        transaction2 = DebitsCredits.objects.create(account=self.account,
                                            date=datetime.datetime.today() - datetime.timedelta(days=28),
                                            name="Buy a 240 USD item",
                                            amount=1,
                                            currency=self.usd)
        transaction2 = DebitsCredits.objects.get(pk=transaction2.pk)
        self.assertEqual(transaction2.amount, 1)
        self.assertEqual(transaction2.reference_amount, None)

        # Now we change the date of change 3
        change3 = Change.objects.get(pk=change3.pk)
        change3.date = datetime.datetime.today() - datetime.timedelta(days=28)
        change3.save()

        transaction2 = DebitsCredits.objects.get(pk=transaction2.pk)
        self.assertEqual(transaction2.amount, 1)
        self.assertEqual(transaction2.reference_amount, 0.08)