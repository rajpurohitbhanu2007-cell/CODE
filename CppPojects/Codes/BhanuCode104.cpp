#include <iostream>
#include <string>
using namespace std;
class calculate{
    
    public:
    void area(double a){
       double d;
       d = 3.14*a*a;
       cout<<"\nCircle Area: "<<d<<endl;
    }
    void area(double a,double b){
       double d;    
       d = a*b;
       cout<<"\nRectangle Area: "<<d<<endl;
    }
    void area(double a,double b,double c){
       double d;    
       d = 2*(a*b+b*c+c*a);
       cout<<"\nCuboid Area: "<<d<<endl;
    }
};
int main(){
    int choice;
    calculate c1;
    double a,b,c;
    
    int q = 1;
    while(q != 0){
    cout<<"Enter Your Choice\n1.Circle\n2.Rectangle\n3.Cuboid"<<endl;
    cin>>choice;    
    if(choice==1){
        cout<<"Circle"<<endl;
        cout<<"Enter the Values: ";
        cin>>a;
        c1.area(a);
    }
    else if(choice==2){
        cout<<"Rectangle"<<endl;
        cout<<"Enter the Values: ";
        cin>>a>>b;
        c1.area(a,b);
    }
    else if(choice==3){
        cout<<"Cuboid"<<endl;
        cout<<"Enter the Values: ";
        cin>>a>>b>>c;
        c1.area(a,b,c);
    }
    else{
        cout<<"ERROR!! Wrong Entry"<<endl;
    }
    cout<<"To Exit Enter 0\nTo Continue Enter Any number"<<endl;
    cin>>q;
    }

    return 0;
}
