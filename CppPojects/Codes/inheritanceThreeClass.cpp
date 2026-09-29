#include<iostream>
using namespace std;

class A{
    protected:
    int rollNo;
    public:
    void input(){
        cout<<"Enter the Roll number : ";
        cin>>rollNo;
    }
    void display(){
        cout<<"The Roll number is : "<<rollNo;
    }
};
class B : public A{
    protected:
    int subject1,subject2;
    public:
    void getData(){
        cout<<"Enter your Marks For both Subjects : ";
        cin>>subject1>>subject2;
    }
    void display(){
        cout<<"Your Marks for Subject 1 is : "<<subject1<<endl;
        cout<<"Your Marks for Subject 2 is : "<<subject2<<endl;
    }
};
class C : public B{
    public:
    void add(){
        cout<<"Total Marks = "<<subject1+subject2;
    }
};

int main(){
    C a;
    a.input();
    a.getData();
    a.display();
    a.add();
}