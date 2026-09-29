#include <iostream>

using namespace std;

class Calculate{
    int x=10;
    int a,b,c,d,e;
    public:
    Calculate(){
        x=100;
        cout<<"Enter Five numbers with space"<<endl;
        cin>>a>>b>>c>>d>>e;
    }
    void add(){
        cout<<"Addition: "<<a+b+c+d+e<<endl;
    }
    void mult(){
        cout<<"Multiplication: "<<a*b*c*d*e<<endl;
    }
};
int main(){
    Calculate a1;
    a1.add();
    a1.mult();
    return 0;
}
