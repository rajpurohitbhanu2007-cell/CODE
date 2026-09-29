#include <iostream>
#include <string>
using namespace std;
class student{
    string name;
    int marks;

    public:
    void getvalue(){
        cout<<"Enter your Name:";
        cin>>name;
        cout<<"Enter your Marks:";
        cin>>marks;
    }
    void printValue(){
        cout<<"Your Name: "<<name<<endl<<"Marks: "<<marks<<endl;
    }
};
int main(){
    student s1;
    
    s1.getvalue();
    cout<<"****************************"<<endl;
    s1.printValue();
    cout<<"****************************"<<endl;
    
    return 0;
}#include <iostream>
#include <string>
using namespace std;
class student{
    string name;
    int marks;

    public:
    void getvalue(){
        cout<<"Enter your Name:";
        cin>>name;
        cout<<"Enter your Marks:";
        cin>>marks;
    }
    void printValue(){
        cout<<"Your Name: "<<name<<endl<<"Marks: "<<marks<<endl;
    }
};
int main(){
    student s1;
    
    s1.getvalue();
    cout<<"****************************"<<endl;
    s1.printValue();
    cout<<"****************************"<<endl;
    
    return 0;
}
