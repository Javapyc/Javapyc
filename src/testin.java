
class Program {

	public static void main(String[] args) {
		System.out.println(1+2);
		System.out.println(10/5);
		System.out.println(Math.pow(2, 4*2) - 1);
		System.out.println(1+2-1);
		System.out.println(1--1+2+-2);
		System.out.println(false && false || false && true || true && true);
		System.out.println(!(1+2 < -1));
		System.out.println(1 == 2);
		System.out.println(1 <= 2 != false && true || false);

		int a = 5+1;
		System.out.println((3+4)*a);
		a = a + 4;
		System.out.println(a);

		//if (10 < 17) System.out.println(5); else System.out.println(4);
		if (true) {int a = 4;} else int r = 3; int t = 34;
		if (false || true) {
		    System.out.println(5 + 6);
		    System.out.println(1 -33);
		} else {
		    System.out.println(-555);
		}

		boolean check = true;
		int count = 0;
		while (check){
			if (count > 5) {check = false;}else{}
			System.out.println(count);
			count = count + 1;
		}
		System.out.println(count);

		if (true) {
		    while (false) int a = 3;
		    System.out.println(5);
		}else{}
		System.out.printf("Hello world");
	}
}

class Null {
}

class ParamTest extends Null {

	int calls;
	public int kevin(boolean r) {
		calls = calls + 1;
		System.out.println(calls); 
		return calls+1; 
	}
	
	public int random() {
		//chosen by fair dice roll, guaranteed to be random
		return 4;
	}

	public int add(int a, int b) {
		int res = a + b;
		return res;
	}
}

