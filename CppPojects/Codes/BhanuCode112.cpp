#include<iostream>
using namespace std;

class student{
    private:
        string name;
        int marks;
    public:
        void input(){
            cout<<"Enter the Name of Student : ";
            cin>>ws;
            getline(cin, name);
            cout<<"Enter the Marks of Student : ";
            cin>>marks;
        }
        void display(){
            cout<<"The Name of Student is : "<<name<<endl;
            cout<<"The Marks of Student is : "<<marks<<endl;
        }
};

int main(){
    int n;
    cout << "Enter number of students : ";
    cin >> n;

    student* s = new student[n];
    for (int i = 0; i < n; i++) {
        s[i].input();
    }

    for (int i = 0; i < n; i++) {
        s[i].display();
    }

    delete[] s;
    return 0;
}