#include <iostream>
#include <string>
using namespace std;
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
    friend void display();
}obj;
void display(){
    cout<<"\nYour Account Number: "<<obj.accountNumber;
    cout<<"\nYour Password: "<<obj.password;
    cout<<"\nYour Name: "<<obj.name;
}
int main() {
    cout << "Program\n";
    obj.getData();
    display();
    return 0;
}
