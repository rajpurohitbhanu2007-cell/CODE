#include <iostream>

using namespace std;

class abc{
    int x=10;
    int a,b,c,d,e;
    public:
    abc(){
        x=100;
        cout<<"Enter Five numbers with space"<<endl;
        cin>>a>>b>>c>>d>>e;
    }
    void show(){
        cout<<x<<endl;
    }
    void add(){
        cout<<"Addition: "<<a+b+c+d+e<<endl;
    }
    void mult(){
        cout<<"Multiplication: "<<a*b*c*d*e<<endl;
    }
};
int main(){
    abc a1;
    a1.show();
    a1.add();
    a1.mult();
    return 0;
}
