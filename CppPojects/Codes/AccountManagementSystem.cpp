#include <iostream>
using namespace std;

class BankAccount {
private:
    double balance;
protected:
    int accountnumber;
public:
    string accountbalance;

    void setBalance(double b) {
        if(b > 0) {
            balance = b;
        } else {
            cout << "Invalid balance" << endl;
        }
    }

    double getBalance() {
        return balance;
    }

    void setAccountNumber(int accNo) {
        accountnumber = accNo;
    }
};

class SavingAccount : public BankAccount {
public:
    void displayAccount() {
        cout << "Account Holder name " << accountbalance << endl;
        cout << "Account Number " << accountnumber << " Account balance " << getBalance() << endl;
    }
};

int main() {
    SavingAccount account1;
    account1.accountbalance = "Rahul"; 
    account1.setAccountNumber(1010);
    account1.setBalance(50000);
    account1.displayAccount();
    
    return 0;
}
