
class Program {
    

	public static void main(String[] args) {

		Base b = new Bob();

		b = new Bob();

        gg t = null;
        
		boolean cond = res > 5;

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
