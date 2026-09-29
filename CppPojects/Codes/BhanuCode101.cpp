#include <iostream>
#include <string>
using namespace std;
struct car{
    string name;
    int topSpeed,milage;
    void getvalue(){
        cout<<"Enter your's Car Name:";
        cin>>name;
        cout<<"Enter your's Car Top Speed:";
        cin>>topSpeed;
        cout<<"Enter your Car Milage:";
        cin>>milage;
    }
    void printValue(){
        cout<<"Your Car's Name: "<<name<<endl<<"Top Speed: "<<topSpeed<<endl<<"Milage "<<milage<<endl;
    }
};
int main(){
    car c1,c2;
    
    c1.getvalue();
    cout<<"****************************"<<endl;
    c1.printValue();
    cout<<"****************************"<<endl;
    c2.getvalue();
    cout<<"****************************"<<endl;
    c2.printValue();
    cout<<"****************************"<<endl;
    
    return 0;
}
