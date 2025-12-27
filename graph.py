# A basic undirected graph class
class Graph:
    numVertices: int
    edges: list

    def __init__(self, numVertices, edges):
        self.numVertices = numVertices
        self.edges = edges

    def addEdge(self, edge):
        if isinstance(edge, Edge):
            return Graph(
                self.numVertices, 
                [*self.edges, edge]
            )
        else:
            raise ValueError("addEdge expects an Edge instance")        

    def removeEdge(self, edge):
        if not isinstance(edge, Edge):
            raise ValueError("removeEdge expects an Edge instance")

        return Graph(
            self.numVertices, 
            [e for e in self.edges if not e.equals(edge)]
        )

    def hasEdge(self, edge):
        if not isinstance(edge, Edge):
            raise ValueError("hasEdge expects an Edge instance")
        for e in self.edges:
            if e.equals(edge):
                return True
        return False

    def getNonSingletonConnectedComponents(self):
        components = set()
        componentsByVertices = {}
        for edge in self.edges:
            [vertex1, vertex2] = edge.getVertices()
            if not id(vertex1) in componentsByVertices and not id(vertex2) in componentsByVertices:
                newComponent = HashableList([vertex1, vertex2])
                componentsByVertices[id(vertex1)] = newComponent
                componentsByVertices[id(vertex2)] = newComponent
                components.add(newComponent)
            elif id(vertex1) in componentsByVertices and not id(vertex2) in componentsByVertices:
                component = componentsByVertices[id(vertex1)]
                componentsByVertices[id(vertex1)] = component
                componentsByVertices[id(vertex2)] = component
                component.append(vertex2)
            elif not id(vertex1) in componentsByVertices and id(vertex2) in componentsByVertices:
                component = componentsByVertices[id(vertex2)]
                componentsByVertices[id(vertex1)] = component
                componentsByVertices[id(vertex2)] = component
                component.append(vertex1)
            else:
                component1 = componentsByVertices[id(vertex1)]
                component2 = componentsByVertices[id(vertex2)]
                if component1 != component2:
                    mergedComponent = HashableList(component1 + component2)
                    for v in mergedComponent:
                        componentsByVertices[id(v)] = mergedComponent
                    components.remove(component1)
                    components.remove(component2)
                    components.add(mergedComponent)
        return components

    def print(self):
        print("Graph with " + str(self.numVertices) + " vertices:")
        for edge in self.edges:
            print(edge.vertex1 + " -- " + edge.vertex2)


# A basic undirected edge class
class Edge:
    def __init__(self, vertex1, vertex2):
        self.vertex1 = vertex1
        self.vertex2 = vertex2

    def getVertices(self):
        return [self.vertex1, self.vertex2]

    def equals(self, otherEdge):
        return (self.vertex1 == otherEdge.vertex1 and self.vertex2 == otherEdge.vertex2) or \
               (self.vertex1 == otherEdge.vertex2 and self.vertex2 == otherEdge.vertex1)

# A hashable list class, where the hash is based on the list id()
class HashableList(list):
    def __hash__(self):
        return id(self)