import streamlit as st
import json

st.set_page_config(
    page_title="Methods",
    layout='wide'
)


with open("project_configuration.json", 'r') as f:
    project_configuration = json.load(f)


st.title("Methods")
st.markdown("The idea of this project was that _if we can automatically, comprehensively annotate many tomograms_, we could summarize large datasets in both a machine and human interpretable way. To do so, we tested a staged approach using multiple convolutional neural networks.")
macromolecules = project_configuration["macromolecules"]
if "Density" in macromolecules:
    macromolecules.remove("Density")
st.markdown(f"In the **first stage** we use **[Ais](https://aiscryoet.org/)** to convert the **input density** volumes into multiple separate **macromolecule segmentations**. Here, the chosen macromolecular structures were _Membranes, ribosomes, RuBisCo, and ATP synthase_.")

with st.expander("Stage 1 details"):
    st.markdown("We trained a separate network for each of the selected macromolecules, and used a sparsely, manually annotated set of images, sampled from across 20 tomograms (~1% of the full dataset) as the training data. For each  network, we limited the preparation time to around 30 minutes annotation. The resulting macromolecule-segmenting models are _far from perfect_, but are nonetheless useful in the next processing stage.")
    st.markdown("Conceptually, the rationale behind this strategy was as follows: if a human is presented with an image that depicts just membranes, ribosomes, and ATP synthase, they are already able to conclude a number of things about the underlying structure. A small circular area enclosed by a membrane and surrounded by ribosomes, for instance, is likely a vesicle or endosome surrounded by cytoplasm. A tubular membrane decorated with ATP synthase is likely to be part of a mitochondrion. Two somewhat parallel membranes with ribosomes on one side and only few distinct macromolecules on the other, probably represents a section of the nuclear envelope. By providing a second layer of neural networks with not just density, but also a number of macromolecule segmentations as the input, we hypothesized that a neural network might more accurately learn to segment and distinguish between more abstract features, or _ontologies_, such as the cytoplasm, mitochondria, nuclear envelope, the Golgi apparatus, vesicles, or chloroplasts.")
    st.markdown("The **network architecture** can be found [here](https://github.com/bionanopatterning/Ais/blob/master/Ais/models/vggnet_l.py). It is a VGGNet with 12 convolutional layers trained using a binary crossentropy loss function.")
    st.markdown("After preparing models on a desktop PC, the segmentations were computed using four Linux systems with 8 CUDA-enabled GPUs each (RTX 3080 and RTX 2080 Ti), requiring on average ~2 seconds per macromolecule per tomogram (note: that is by virtue of running 32 parallel processes; on a single GPU, processing a single volume costs in ~70 seconds). The tomograms were binned by a factor 2, to a size of 512 x 512 x 256 voxels.")
    st.code("ais segment -m /models/15.68_64_0.0261_Membrane.scnm -d /full_dataset -ou /macromolecules -gpu 0,1,2,3,4,5,6,7")

ontologies = project_configuration["ontologies"]
st.markdown(f"The **second stage** comprises the preparation of multiple separate neural networks that each segment one particular [(ontology-based)](https://geneontology.org/docs/ontology-documentation/) organelle, using **macromolecule segmentations and density as the input.** Here, the chosen organelles and other subcellular features were _{', '.join(o for o in ontologies[:-1])}, and {ontologies[-1]}_. In order to prepare separate training datasets for each feature, we used **[Ais](https://aiscryoet.org/)** to sparsely annotate the chosen organelles across the full dataset.")
with st.expander("Stage 2 details"):
    st.markdown("We use the term organelle to refer to ane _distinct compartment, structure, location, or other  abstract area of interest_ in the way that these often makes up a core concept in a cryoET project. Whichever structure is studied, certain specific organelles represent that study's areas of interest, while others organelles represent regions of the sample that may be irrelevant. For example, when studying chromatin, we typically need not search for it the cytoplasm. If it is feasible to automatically annotate many different ontologies in a large dataset, it should thus be possible to filter and select parts of the dataset that are the most relevant for a particular study, while reducing the time spent studying volumes or subtomograms that are less likely to contain useful information. Concretely, we envision two main use cases. First, to automatically select subsets of large datasets, by filtering based on the ontology content and quality metrics. Second, to use ontological segmentations to generate masks for template matching or particle picking. Other possible applications may be quantitative studies on the composition of cells or prevalence of certain compartments, or enriching the metadata of a particle sets by characterizing the local environment within which a particle was found (e.g. nuclear vs. chloroplast vs. cytosolic ribosomes)")
    st.markdown("**Void**: this is the name that we use to refer to ill-defined densities in tomograms. The most prevalent representation of void is found in the top and bottom of reconstructed volumes, when the reconstruction depth is larger than the actual thickness of the imaged area. Besides annotating these regions as void, we also considered reconstruction artefacts, blurry image regions, and large empty areas of the sample void. As a result, the void segmentations provide an indication not only of the boundaries of the lamella within the reconstructed volume, but also of the quality of a tomogram.")
    st.markdown("The **network architecture** was similar to that used in step 1, but with a number of dilating kernels used in the last encoding layers.")

    st.code("pom single initialize   # parse training data for all ontologies")
    st.code("pom single train -ontology Cytoplasm -gpus 0,1,2,3,4,5,6,7   # train one of the models")
    st.code("pom single test -ontology Cytoplasm -gpus 0,1,2,3,4,5,6,7   # optionally, test models on a selected set of tomograms")

st.markdown(f"The **third and last stage** is to train a single, combined model, which outputs segmentations for all selected organelles. By applying all previously prepared single-feature networks to all the single-feature training datasets, and combining the results, we prepared a joint training dataset that consisted of close to 4000 training images. We then trained a final model to output all organelles at once, based on the segmented  macromolecules and density images as the input. This model was  deployed on four Linux PCs with 8 CUDA-enabled GPUs each. Processing the full dataset took **just under 1 hour**, at an average segmentation time of around 2 seconds per tomogram.")

with st.expander("Stage 3 details"):
    st.markdown("Any combination of macromolecule and density inputs and organelle outputs can be selected to train a network for. Although we used all macromolecules _and_ density here, it might be interesting to test how accurately a network can get if it is trained on macromolecules but _not on density_. If this would work, the resulting networks might be more-or-less density-agnostic, and thus perhaps more suited for reuse with different datasets. If so, it might be possible to automate a part of stage 1 by using specialized systems such as [MemBrain](https://github.com/teamtomo/membrain-seg) to prepare the macromolecule segmentations. Or perhaps going from density straight to organelles may be more practical, since a single network should also be able to achieve what a combination of different networks can. The challenge, however, is always to prepare suitable training data - in our experience, the limiting factor in segmentation throughput and accuracy is not the network architecture, but rather the amount of time one can spare to annotate the training data.")
    st.markdown("We used a UNet **network architecture** with 18 convolutional layers, three skip connections, and a softmax output layer, trained using categorical cross-entropy loss and one-hot encoded training output.")

    st.code("pom shared initialize   # parse & segment all training data for all ontologies")
    st.code("pom shared train -gpus 0,1,2,3,4,5,6,7  # train the joint model")
    st.code("pom shared process -gpus 0,1,2,3,4,5,6,7  # process data")

st.markdown(f"Once all segmentations are complete, a summary and lots of representative images (~75k) can be generated using Pom (which internally uses Ais). Finally, the results can be browsed in a streamlit app (which is the web page you are looking at right now).")

with st.expander("Summary details"):
    st.code("pom summarize   # measure volume fractions for all segmented features and write to an .xlsx file")
    st.code("pom projections   # output xy and xz projection images of all ontology segmentations")

    st.code("pom render -s render_configuration.json   # batch-output 3D rendered images showing ontologies and/or macromolecules as defined in render_configuration.json")
    st.code("pom browse   # launch the data browser")

st.markdown("A pre-print where we describe Pom and its use in 1) curating data, 2) context-aware particle picking, and 3) improving the speed of template matching up to 500-fold using _area-selective_ template matching, will be available soon.")
st.markdown("Contact: mgflast@gmail.com")
