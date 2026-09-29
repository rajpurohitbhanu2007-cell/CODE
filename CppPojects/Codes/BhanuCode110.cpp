#include <iostream>
#include <string>
using namespace std;

class displayBankInfo{
public:    
void display();
}b1;

class BankInfo{
    int a = 10;
    long int accountNumber;
    int password;
    string name;
    public:
    void getData(){
        cout<<"Enter Account Number: ";
        cin>>accountNumber;
        cout<<"Enter Password: ";
        cin>>password;
        cout<<"Enter name: ";
        cin>>name;
    }
    friend void displayBankInfo::display();
}a1;
void displayBankInfo::display(){
    cout<<"\nYour Account Number: "<<a1.accountNumber;
    cout<<"\nYour Password: "<<a1.password;
    cout<<"\nYour Name: "<<a1.name;
}
int main() {
    cout << "Program\n";
    a1.getData();
    b1.display();
    return 0;
}
