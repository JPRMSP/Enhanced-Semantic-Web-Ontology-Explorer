import streamlit as st
from rdflib import Graph, RDF, RDFS, OWL
import networkx as nx
from pyvis.network import Network
import tempfile

st.set_page_config(page_title="Enhanced Ontology Explorer", layout="wide")
st.title("Enhanced Semantic Web Ontology Explorer 🌐")

# Input ontology
ontology_url = st.text_input("Enter ontology URL (OWL/RDF/XML):", "https://www.w3.org/2002/07/owl")

if ontology_url:
    g = Graph()
    try:
        g.parse(ontology_url)
        st.success("Ontology loaded successfully!")

        # Extract classes and properties
        classes = set(g.subjects(RDF.type, OWL.Class))
        properties = set(g.subjects(RDF.type, RDF.Property))

        st.subheader("Ontology Summary")
        st.write(f"Total Classes: {len(classes)}")
        st.write(f"Total Properties: {len(properties)}")

        # Display class hierarchy
        st.subheader("Class Hierarchy Visualization")
        G = nx.DiGraph()
        for c in classes:
            for subclass in g.objects(c, RDFS.subClassOf):
                G.add_edge(str(subclass), str(c))

        net = Network(height="600px", width="100%", notebook=False, directed=True)
        for node in G.nodes:
            net.add_node(node, label=node, title=f"Subclasses: {len(list(G.successors(node)))}")
        for edge in G.edges:
            net.add_edge(edge[0], edge[1])
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        net.show(temp_file.name)
        st.components.v1.html(open(temp_file.name, 'r', encoding='utf-8').read(), height=600, scrolling=True)

        # Class-property explorer
        st.subheader("Class Property Explorer")
        selected_class = st.selectbox("Select a class to view properties", list(classes))
        class_properties = []
        for prop in properties:
            domains = list(g.objects(prop, RDFS.domain))
            ranges = list(g.objects(prop, RDFS.range))
            if selected_class in domains:
                class_properties.append((str(prop), [str(d) for d in domains], [str(r) for r in ranges]))
        if class_properties:
            for prop, dom, ran in class_properties:
                st.write(f"Property: {prop} | Domain: {dom} | Range: {ran}")
        else:
            st.write("No properties found for this class.")

        # Interactive relationship search
        st.subheader("Find Relationship Between Classes")
        class1 = st.selectbox("Class 1", list(classes))
        class2 = st.selectbox("Class 2", list(classes))
        found = False
        for prop in properties:
            domains = list(g.objects(prop, RDFS.domain))
            ranges = list(g.objects(prop, RDFS.range))
            if class1 in domains and class2 in ranges:
                st.success(f"Relationship found: {class1} -- {prop} --> {class2}")
                found = True
        if not found:
            st.info("No direct relationship found.")

        # Sample RDF triples
        st.subheader("Sample RDF Triples")
        triples_sample = list(g)[:20]
        for s, p, o in triples_sample:
            st.write(f"{s} -- {p} --> {o}")

        # Optional SPARQL queries
        st.subheader("Run SPARQL Query")
        sparql_query = st.text_area("Enter SPARQL query:", "SELECT ?s ?p ?o WHERE {?s ?p ?o} LIMIT 10")
        if st.button("Run Query"):
            try:
                results = g.query(sparql_query)
                for row in results:
                    st.write(row)
            except Exception as e:
                st.error(f"SPARQL Query Error: {e}")

    except Exception as e:
        st.error(f"Failed to load ontology: {e}")
