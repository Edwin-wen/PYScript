class Node:
    def __init__(self, data):
        self.data = data
        self.childList = []
        self.parentList = []

    def add_child(self, childParam):
        self.childList.append(childParam)

    def add_parent(self, parentParm):
        self.parentList.append(parentParm)

    def remove_child(self, childParam):
        for i in range(len(self.childList))[::-1]:
            if self.childList[i].data == childParam.data:
                del self.childList[i]

    def remove_parent(self, parentParam):
        for i in range(len(self.parentList))[::-1]:
            if self.parentList[i].data == parentParam.data:
                del self.parentList[i]

    def have_child(self):
        return len(self.childList) > 0

    def have_parent(self):
        return len(self.parentList) > 0

    def getChild(self, data):
        for child in self.childList:
            if child.data == data:
                return child
            else:
                curChild = child.getChild(data)
                if curChild is not None:
                    return curChild
        return None

    def getParent(self, data):
        for parent in self.parentList:
            if parent.data == data:
                return parent
            else:
                curParent = parent.getParent(data)
                if curParent is not None:
                    return curParent
        return None

    def isHead(self):
        return not self.have_parent()

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.data) + "\n"
        for child in self.childList:
            ret += child.__repr__(level + 1)
        return ret

def addNodeToTree(headNode, childData, parentData):
    parentNode = headNode.getChild(parentData)
    if parentNode is None: # 如果父节点不在tree中，加到head的子树里
        parentNode = Node(parentData)
        childNode = Node(childData)
        childNode.add_parent(parentNode)
        headNode.add_child(parentNode)
    else:
        childNode = parentNode.getChild(childData)
        # 如果父节点在tree中，但子节点不在tree中，新建子节点
        if childNode is None:
            childNode = Node(childData)
            childNode.add_parent(parentNode)

    # 处理子节点应该挂在哪里
    originChildNode = headNode.getChild(childData)
    if originChildNode is not None:
        originParentNode = originChildNode.getParent(parentData)
        # 处理新加入的父子节点都在tree中的情况
        if originParentNode is not None:
            originParentNode.remove_child(originChildNode)
            originParentNode.add_child(parentNode)
        # 子节点在tree中，但往上没找到新加入的父节点，说明是在根节点的子树，直接移除掉
        else:
            headNode.remove_child(originChildNode)
        parentNode.add_child(originChildNode)
    else:
        parentNode.add_child(childNode)

    return headNode

if __name__ == '__main__':
    head = Node('wps')
    addNodeToTree(head, 'child1', 'parent1')
    addNodeToTree(head, 'child2', 'parent1')
    addNodeToTree(head, 'child2', 'parent2')
    addNodeToTree(head, 'child3', 'child1')
    addNodeToTree(head, 'child4', 'child1')
    addNodeToTree(head, 'child5', 'child2')
    addNodeToTree(head, 'child6', 'child2')
    addNodeToTree(head, 'parent2', 'parent3')
    addNodeToTree(head, 'child7', 'child6')
    print(head)