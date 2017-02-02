// TernarySearchTree.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include<string>
#include<iostream>
#include<cstdio>
using std::string;
using std::cout;
using std::endl;
using std::cin;

class Node {
public:
	char c;
	bool terminal;
	Node* lo;
	Node* mi;
	Node* hi;
	Node(char c):c(c),terminal(false),lo(nullptr),mi(nullptr),hi(nullptr) {}
};

class Tree {
private:
	Node* root;
public:
	Tree():root(nullptr) {}
	//add a new string to the tree
	void add(string str);
	//search for a given string
	bool search(string str);
	//inspect the tree structure
	void print();
	void print(Node* node);
	void add2(string str);
};

void Tree::print() {
	Tree::print(this->root);
}

void Tree::print(Node* node) {
	if (node != nullptr) {
		cout << "printing: " << node->c << endl;
		print(node->lo);
		print(node->mi);
		print(node->hi);
	}
}

void Tree::add(string str) {
	cout << "adding " << str << endl;
	if (str.empty()) {
		return;
	}

	if (root == nullptr) {
		root = new Node(str[0]);
	}
	Node* cur = root;
	int i = 0;
	while (i < str.size()) {
		if (cur == nullptr) {
			cur = new Node(str[i]);
			if (i == str.size() - 1) {
				cur->terminal = true;
				return;
			}
			cur = cur->mi;
			++i;
		}
		else {
			if (str[i] < cur->c) {
				if (cur->lo == nullptr) {
					cur->lo = new Node(str[i]);
					if (i == str.size() - 1) {
						cur->lo->terminal = true;
						return;
					}
					cur = cur->lo;
					++i;
					while (i < str.size()) {
						if (cur->mi == nullptr) {
							cur->mi = new Node(str[i]);
							if (i == str.size() - 1) {
								cur->mi->terminal = true;
								return;
							}
							cur = cur->mi;
							++i;
						}
					}
				}
				else {
					cur = cur->lo;
				}
			}
			else if (str[i] > cur->c) {
				if (cur->hi == nullptr) {
					cur->hi = new Node(str[i]);
					if (i == str.size() - 1) {
						cur->hi->terminal = true;
						return;
					}
					cur = cur->hi;
					++i;

					while (i < str.size()) {
						if (cur->mi == nullptr) {
							cur->mi = new Node(str[i]);
							if (i == str.size() - 1) {
								cur->mi->terminal = true;
								return;
							}
							cur = cur->mi;
							++i;
						}
					}
				}
				else {
					cur = cur->hi;
				}
			}
			else {
				if (i == str.size() - 1) {
					cur->terminal = true;
					return;
				}

				while (i < str.size()) {
					if (cur->mi == nullptr) {
						++i;
						cur->mi = new Node(str[i]);
						if (i == str.size() - 1) {
							cur->mi->terminal = true;
							return;
						}
						cur = cur->mi;
					}
					else {
						if (i == str.size() - 1) {
							cur->terminal = true;
							return;
						}
						cur = cur->mi;
						++i;
					}
				}
			}
		}
	}
}

bool Tree::search(string str) {
	Node* cur = this->root;
	int i = 0;
	while (i < str.size()) {
		if (cur == nullptr) {
			return false;
		}

		if (i == str.size() - 1 && cur->terminal == true) {
			return true;
		}

		if (str[i] < cur->c) {
			cur = cur->lo;
		}
		else if (str[i] > cur->c) {
			cur = cur->hi;
		}
		else {
			cur = cur->mi;
			++i;
		}
	}
	return false;
}



int main()
{
	Tree* tree = new Tree();
	tree->add("yes");
	tree->add("yet");
	tree->add("ab");
	tree->add("ye");
	tree->add("abd");

	cout << "done adding" << endl;



	cout << tree->search("yes") << "," << tree->search("yet") << "," << tree->search("ab")<<","<<tree->search("ye")<<","<<tree->search("abd") << endl;
	std::getchar();
	return 0;
}

