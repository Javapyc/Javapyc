
class Program {
    

	public static void main(String[] args) {

		Base b = new Bob();

		b = new Bob();

        Bob t = new Bob();

        int res = 89;
        
		boolean cond = res > 5;

        while(cond){
            int f = 45;
            f = f - 9;
        }

		if (cond && true) {
			int a = 5;
			System.out.printf("4 + 5 = %d\n", res);
			System.out.println(a + 1);
		} else {
			System.out.println(42);
		}
	}

}

class Base {

    boolean classvar;
    boolean classvar;

	public int add(int a, int b) {
		return a + b;
	}
}

class Bob extends Base{

	public int add5(int a) {
		return a + 5;
	}
}
