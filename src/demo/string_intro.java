
class Program {
	public static void main(String[] args) {

		int a = 22;
		int b = 20;

		System.out.printf("%d + %d = %d\n", a, b, a+b);

		System.out.printf("%s\n", new Dog().setName("Bob"));
	}
}

class Dog {

	String name;

	public Dog setName(String newName) {
		name = newName;
		return this;
	}

	public String getSpecies() {
		return "dog";
	}

	public String toString() {
		return String.format("%s is a %s", name, this.getSpecies());
	}
}
