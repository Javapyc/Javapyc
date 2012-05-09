
class Main {
	public static void main(String[] args) {
		Program prog = new Program();
		int main1 = prog.setValue(10); //10
		int main2 = prog.shadow(main1 + 5); //30

		System.out.println(main1); //10
		System.out.println(main2); //30
		System.out.println(prog.getValue()); //10
	}
}

class Program {

	int mystery;

	public int setValue(int n) {
		mystery = n;
		return mystery;
	}
	
	public int getValue() {
		return mystery;
	}

	public int shadow(int n) {
		int mystery = n;
		mystery = mystery * 2;
		return mystery;
	}
}

