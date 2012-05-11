
class Main {
	public static void main(String[] args) {

		{
			Dog bob = new Dog();
			bob.setName("Bob");
			
			Dog steve = new Labrador();
			steve.setName("Steve");
			
			Animal unknown = new Animal();

			System.out.printf("Bob: %s\n", bob);
			System.out.printf("Steve: %s\n", steve);
			System.out.printf("Unknown: %s\n", unknown);

			unknown = steve;
			System.out.printf("Steve: %s\n", unknown);
		}

		{
			Tree tree = new Tree();
			tree.init();
			tree.add(10);
			tree.add(5);
			tree.add(3);
			tree.add(4);
			tree.add(15);
			System.out.printf("\n%s", tree);
		}
	}
}

class Animal {

	public String getSpecies() {
		return "Unknown";
	}
	
	public String toString() {
		return this.getSpecies();
	}
}

class Dog extends Animal {
	String name;

	public String setName(String newName) {
		name = newName;
		return name;
	}

	public String getSpecies() {
		return "dog";
	}

	public String toString() {
		return String.format("%s is a %s", name, this.getSpecies());
	}
}

class Labrador extends Dog {
	public String getSpecies() {
		return "labrador";
	}
}

class Tree {

	Node mRoot;

	public Tree init() {
		mRoot = new LeafNode();
		return this;
	}

	public boolean add(int value) {

		if (mRoot.isLeaf()) {
			mRoot = this.createNode(value, mRoot, mRoot);

		} else {
			mRoot.add(value);
		}

		return true;
	}

	public Node createNode(int value, Node left, Node right) {
		return new ValueNode().initialize(value, left, right);
	}
	
	public Node createLeafNode(int value) {
		return new LeafNode();
	}

	public String toString() {
		return String.format("%s", mRoot);
	}
}

class Node {

	int mDepth;

	public boolean isLeaf() {
		return false;
	}

	public Node add(int value) {
		return this;
	}

	public int setDepth(int depth) {
		mDepth = depth;
		return mDepth;
	}
	
}

class LeafNode extends Node {

	public boolean isLeaf() {
		return true;
	}
	
	public Node add(int value) {
		return new ValueNode().initialize(value, this, this);
	}
	
	public String toString() {
		return "-";
	}

}

class ValueNode extends Node {

	int mValue;

	Node mLeft;
	Node mRight;

	public Node initialize(int value, Node left, Node right) {
		mValue = value;
		mLeft = left;
		mRight = right;

		return this;
	}
	
	public Node add(int value) {
		if (value != mValue) {
			if (value < mValue) {
				mLeft = mLeft.add(value);
			} else /* (value > mValue) */ {
				mRight = mRight.add(value);
			}
		} else {
		}

		return this;
	}

	public int getValue() {
		return mValue;
	}

	public String indent(String s, int depth) {
		if (depth > 0) {
			s = this.indent(String.format(" %s", s), depth-1);
		} else {
		}

		return s;
	}

	public String toString() {
		mLeft.setDepth(mDepth+1);
		mRight.setDepth(mDepth+1);
		return String.format("(%d\n%s\n%s)",
				mValue,
				this.indent(String.format(" %s", mLeft), mDepth),
				this.indent(String.format(" %s", mRight), mDepth));
	}
}
