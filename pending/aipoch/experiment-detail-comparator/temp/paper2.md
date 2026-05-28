

## Page 1

www.nature.com/cddis
ARTICLE OPEN
EGR4 transcriptionally upregulates GDF15 to promote gastric
cancer metastasis
Weiwei Liu1,2,4, Yanyan Li2,4,Lixin Liang3,4, LishengZheng1,4, Rui Zeng2, Congcong Zhang2,Zhihao Lin2,WanyingFeng1 and
✉
Qingling Zhang1,2
©TheAuthor(s)2025
Gastriccancer(GC)metastasisremainsamajorcauseofpoorprognosis,yetitsmoleculardriversarepoorlyunderstood.Here,we
integratedsingle-cellRNAsequencing(scRNA-seq)ofprimarytumorsandmatchedmetastaticlymphnodesfromsixGCpatientsto
identifyametastaticepithelialsubpopulationcharacterizedbyEGR4overexpression.Kaplan-MeieranalysisrevealedthathighEGR4
expressioncorrelatedwithreducedsurvivalinGCpatients.Mechanistically,chromatinimmunoprecipitationsequencing(ChIP-seq)
andluciferase assays demonstrated that EGR4 directly boundtothe GDF15promoter, drivingits transcriptional activation.
Functionalstudies showedthat EGR4 promoted migration and metastasis via GDF15-mediatedErbB3/ErbB1 hetero-dimerization,
whichactivated PI3K/AKT and MAPK/ERKpathways. Furthermore, CellChatanalysisidentifiedrobust interactions betweenEGR4+
GCcells andcancer-associated fibroblasts (CAFs),particularly extracellular matrix (ECM)-remodeling eCAFs. Secreted GDF15
inducedCAF activationthrough TGF-βreceptor signaling,creatinga pro-metastatic niche. Collectively, our study establishes the
EGR4/GDF15axis asa critical driverof GCmetastasis, offeringpossible therapeutic targets forintervention.
CellDeathand Disease (2025) 16:807 ; https://doi.org/10.1038/s41419-025-08095-w
INTRODUCTION cancers [16, 17]. It promotes cell growth through transcriptional
Gastric cancer (GC) is a common malignancy worldwide, with pathways in small cell lung cancer [18]. In non-small cell lung
approximately 1 million newly diagnosed cases each year [1, 2]. cancer, EGR4 promotes tumor growth through interacting with
Despite advancements in diagnosis and treatment in the past longnon-codingRNAZNF205-AS1inapositivefeedbackmanner
decades, the prognosis for advanced GC remains poor, with an [19]. However, downregulation of EGR4 inhibits cholangiocarci-
overall survival rate of only around 40% [3–5]. Metastasis is an noma tumor cell growth [20]. Up to now, the role of EGR4 in GC
important cause of treatment failure in GC [6]. However, the metastasis and itsmechanismremain unclear.
mechanisms underlying GC metastasis and its biomarker remain In this study, we found that EGR4+ cancer cells play a pivotal
unclear. role in GC metastasis by upregulating GDF15, which can bind
Single-cell RNA sequencing (scRNA-seq) is a powerful tool ErbB3 to enhance ErbB3/ErbB1 hetero-dimerization and the
providing expression profiles of human cancers and tumor activationofErbB1anditsdownstreamMAPK/ERKandPI3K/AKT
microenvironment (TME) cells at single-cell resolution, enabling to signaling, while induce CAFs activation via the TGF-βR pathway
identifyandcharacterizespecificsub-clusterswithuniquebiological to in turn further promote GC metastasis. Our study highlights
functions, which has been widely adopted in cancer research to the critical role of EGR4/GDF15 axis in GC metastasis, under-
explore the TME and tumor cell evolution [7–9]. Lymphatic scores its potential as a prognosis biomarker and therapeutic
metastasis is the most common form of GC metastasis, occurring target of GC.
in both early and advanced GC, affecting its prognosis and
treatmentdecision[10–12].Therefore,weanalyzedscRNA-seqdata
MATERIALSANDMETHODS
of GC tissues and paired metastatic lymph nodes to investigate
genes involved in GC metastasis, and identified the enrichment of Patient andsample collection
EGR4+cancercellsassociatedwithpoorprognosisinmetastases. HumanGCsurgicalsamples(12cases,withpatientinformationshownin
Supplementary Table 1) were collected from Guangdong Provincial
EGR4, one of the early growth response (EGR) transcription
People’s Hospital and paraffin-embedded specimens (tissue micro array,
factor family, plays crucial roles in embryonic development,
TMA)werepurchasedfromTaizeBiotechnologyCo,withatotalof72cases
nervous system development, and adult physiology [13–15]. andthepatientinformationshowninsupplementaryTable2.Thisstudy
Functioning as a transcription factor, EGR4 regulates the expres- wasapprovedbythehospital’sethicscommittee(ID:KY2025-458-01)and
sion of various targeted genes and plays diverse roles in various allparticipantsprovidedwritteninformedconsent.
1DepartmentofPathology,GuangdongProvincialPeople’sHospital(GuangdongAcademyofMedicalSciences),SouthernMedicalUniversity,Guangzhou,Guangdong,China.
2GuangdongProvincialKeyLaboratoryofArtificialIntelligenceinMedicalImageAnalysisandApplication,GuangdongProvincialPeople’sHospital,GuangdongAcademyof
MedicalSciences,Guangzhou,China.3DepartmentofOralPathology,GuangdongProvincialKeyLaboratoryofStomatology,HospitalofStomatology,SunYat-senUniversity,
Guangzhou,People’sRepublicofChina.4Theseauthorscontributedequally:WeiweiLiu,YanyanLi,LixinLiang,LishengZheng. ✉ email:zhangqingling@gdph.org.cn
EditedbyProfessorGennaroCiliberto
Received:14March2025Revised:24August2025Accepted:17September2025
OfficialjournalofCDDpress
:,;)(0987654321

## Page 2

W.Liuetal.
2
Celllines andculture 1–4µg of antibody overnight at 4°C. Unbound proteins were removed
HumanGCcelllinesHGC27andMKN45werepurchasedfromtheATCC bywashingthricewithlysisbufferorPBS.Afterelution,immunoblotting
cellbank,andhumanGCtissue-derivedfibroblastswerepurchasedfrom wasperformedusingspecificprimaryantibodies.Theantibodydetailsand
Shenzhen Youli Biotechnology Co. HGC27 cells were cultured in DMEM dilutionmultipleareprovidedinSupplementaryTable3.
high-glucose medium (Procell, Cat#PM150110) with 10% fetal bovine
serum(FBS;Sigma-Aldrich,Cat#F0193),whileMKN45cellswereculturedin
Plasmids,siRNA, shRNA andtransfection
RPMI-1640 (Procell, Cat#PM150110) complete medium with 10% FBS.
Fibroblasts were cultured in iCell primary fibroblast-specific medium Wild-typeandmutantFlag-EGR4plasmidswerepurchasedfromGuangz-
(Procell,Cat#CM-h206).AllcellsweremaintainedinT25flasksat37°Cwith hou Hanyi Biotechnology Co. ShRNA and siRNA specially targetingEGR4
and GDF15 were synthesized by Guangzhou Jiyuan Biotechnology Co.
5%CO inanincubatorwiththemediumreplacedeverytwodays.
2 PlasmidandsiRNAweretransfectedusingLipofectamine3000(Invitrogen,
USA).SequencesofsiRNAandshRNAarelistedinSupplementaryTable5.
Western blotanalysis
CellswerefirstlysedinRIPAbuffer(ECOTOPSCIENTIFIC,Cat#ES-8148-100)
ELISA
containingproteaseandphosphataseinhibitors(NCM,Cat#P003)onicefor
30min. And then, cell lysates were clarified through centrifugation at The GDF15 concentration was measured with the ELISA kit (HBDY,
Cat#HBDY-1643H2). Briefly, the plates were first equilibrated at room
12,000g at 4°C for 20min and equal mass of proteins (20µg) were
temperature for 20min. Standards and samples were then added to
separated by SDS-PAGE, following by transferred to PVDF membranes
(Millipore, USA) throughBio-Rad’s wet transfer system. Membranes were designated wells, followed by HRP-conjugated detection antibody. After
first blocked in TBST with 5% BSA and then incubated with appointed incubation at 37°C for 60min, the plates were washed thrice, and
substrateAandBwerethenadded.After15minofincubationat37°Cin
primaryantibodies.AfterwashingthricewithTBST,themembraneswere
the dark, the reaction was stopped, and absorbance was measured at
thenincubatedwithcorrespondingHRP-conjugatedsecondaryantibodies
450nm.
at room temperature for 1h. Finally, the proteins were visualized using
GelView 6000 Plus (BLT Photon Technology, China) according to the
manufacturer’s instructions. All experiments were repeated three times Transwellmigration andinvasion assay
with the antibody information and dilution multiple provided in Cells in 200µL FBS free medium (1×105cells/mL) were seeded in the
SupplementaryTable3.Relativeproteinexpressionlevelswerequantified upper chamber of a 24-well transwell plate (CORNING,Cat#353097), with
usingImageJsoftwareversion1.54p. thelowerchambercontainingmediumwith10% FBSas achemoattrac-
tant.Forinvasionassay,thecellswereplatedintheMatrigelpre-coated
upperchamber.After24–72hincubationat37°Cwith5%CO ,thecells
Immunohistochemistry werefixedwithmethanolandnon-migrated/invadedcellswere 2 removed,
Tissueswerefixedandembeddedinparaffin,and3µm-thicksectionswere
andmigrated/invadedcellswerestainedwith0.1%crystalviolet.Cellsin
prepared. After de-paraffinization, antigen retrieval using EDTA antigen fiverandomfieldswerecounted.
retrieval solution (biosharp, Cat#BL617A) and endogenous peroxidase
activity quenching with hydrogen peroxide, the sections were then
washed three times with PBS and the non-specific binding sites were Subcutaneoustumorformationandlungmetastasismodelin
blockedwith5%goatserumatroomtemperaturefor1h.Thereafter,the nudemice
sections were incubated with primary antibodies at 4°C overnight, MKN45cells(1×106cells)weresuspendedin100µLserum-freemedium
followed by three washes with PBS and then incubated with HRP- andinjectedsubcutaneouslyintotheflankoffour-week-oldmaleBALB/c
conjugatedcorrespondingsecondaryantibodiesatroomtemperaturefor nude mice (n=5 per group) (purchased from Guangdong Medical
1h.AfterthreewasheswithPBS,thesectionsweredevelopedusingaDAB Laboratory Animal Center) weighing 15–20g. Two weeks later, the mice
kit (ZSGB-BIO, Cat#ZLI-9019) for 5–10minuntil the desired color was wereeuthanizedandthetumorswereharvestedforhistologicalanalysis.
observed.Afterwards,thenucleiwerecounterstainedbyhematoxylin,and Formetastasismodel,MKN45cells(1×106cells)weresuspendedin100µL
thensectionsweredehydrated,clearedandmounted.Finally,imageswere ofserum-freemediumandinjectedintothetailveinoffour-week-oldmale
captured using a microscope and analyzed with ImageJ software. The BALB/c nude mice. Mice were monitored weekly for body weight and
antibodyinformationanddilutionmultipleareprovidedinSupplementary general health. After five weeks, the mice were euthanized and lung
Table3. tissueswereharvestedtoassessmetastaticnodules.Animalswerekeptin
theSPFanimalbreedingroomofDaokeBiological(Guangzhou,China).All
operations were carried out in accordance with relevant guidelines and
Immunofluorescence analysis regulationsandwereapprovedbytheAnimalEthicsCommittee(number:
Multiplex staining was performed using the PANO 7-plex IHC kit (CAT KY2025-458-01).
0004100100, Panovue, Beijing, China). Sections were sequentially incu-
batedwithappointedprimaryantibodies,HRP-conjugatedcorresponding
secondary antibodies and tyramide signal amplification (TSA) substrates. ChIP-seq andChIP-qPCR
AftereachroundofTSAtreatment,sectionsweresubjectedtomicrowave Fresh cells were cross-linked in 1% formaldehyde, and the reaction was
heat treatment. Nuclei were stained with DAPI after all antigens were quenched with 125mM glycine. Chromatin was then sheared to
labeled. The antibody information and dilution multiple are provided in 100–500bp fragments using sonication. Flag antibody (1–5µg) was
SupplementaryTable3. incubated with chromatin fragments overnight at 4°C and protein A/G
beads (Beyotime,Cat#P2181S) (1–5µg) were then added to incubate for
additional 4–6h at 4°C. Beads were sequentially washed with low-salt,
RT-qPCRanalysis high-salt,LiCl,andTEbuffers,andthenDNAwaselutedwith1%SDSand
TotalRNAwasfirstextractedusingtheTRIzolreagent(AG,Cat#AG21102), 0.1MNaHCO3.Aftercrosslinkreversalat65°Covernight,DNAwaspurified
and then measured with NanoDrop to detect RNA concentration and using Qiagen DNA extraction kit. DNA was analyzed by qPCR or
purity.RNAwasreverse-transcribedusingareversetranscriptionkit,and sequencing. For ChIP-qPCR assay, DNA was analyzed using SYBR Green
SYBRGreenPCRMasterMix(AG,Cat#AG11718)wasusedforamplification
onaQuantStudio5qPCRsystem.Experimentswererepeatedthreetimes,
on LightCycler 480 Fast Real-Time PCR system (Roche). The reaction andtheprimersequencesarelistedinSupplementaryTable4.Datawere
consistedof40cyclesof95°Cfor10sandthen60°Cfor30s.GAPDHwas analyzed using two-tailed t-tests, with P<0.05 considered statistically
usedasaninternalcontrol,andgeneexpressionwasanalyzedusingthe significant.
2-ΔΔCtmethod.TheprimersequencesarelistedinSupplementaryTable4.
Dual-luciferase reporterassay
Immunoprecipitation Wild-typeandmutantGDF15promoterweresynthesizedandinsertedinto
Cellswerewashedtwicewithice-coldPBSandthenlysedinlysisbuffer the pGL3-basic vector (Promega). The plasmids were co-transfected with
containing protease and phosphatase inhibitors and PMSF (ECOTOP Renilla luciferase expression plasmid (Promega) into cells using Lipofecta-
SCIENTIFIC,Cat#ES-8134-10).Celllysateswereincubatedonicefor30min mine2000.Fortyeighthourslater,theluciferaseactivitywasthenmeasured
and centrifuged at 12,000g at 4°C for 30min. Equal lysates were using a dual-luciferase reporter kit (TransDetect, Cat#fr201-02-v2), and
incubated with fresh protein A/G beads (Beyotime,Cat#P2181S) and signalsweredetectedusingaInfiniteM200PROplatereader.
CellDeathandDisease (2025) 16:807

## Page 3

W.Liuetal.
3
RNAsequencing lymphnodesexhibitedsignificantlyhigherCNVlevelsthanthose
TotalRNAwasfirstextractedusingtheTRIzolreagent(Invitrogen),andthe in primary tumors (Fig. 1F). Among all the 10 epithelial cell
Poly(A) RNA was enriched and fragmented using the magnesium RNA clusters,theC3clusterhadlowestCNVlevels(Fig.1G),suggesting
fragmentation module at 94°C. RNA was then reverse-transcribed into that the C3 cluster represented a population of normal gastric
cDNA using SuperScript™ II reverse transcriptase and sequenced on an
epithelial cells, while the other clusters representing malignant
Illumina Novaseq™ 6000. Transcript expression was analyzed using
epithelialcells[21,22].Todissecttheevolutionarydynamicsofthe
StringTieandedgeR,anddifferentiallyexpressedgenes(log2foldchange
>1or<−1,P<0.05)wereidentified.Volcanoplotswereusedtovisualize gastricepitheliallineage,apseudo-timetrajectoryanalysisforthe
differentially expressed genes, and Gene Ontology (GO) analysis was 10epithelialcellclusterswasperformed,generatingafour-branch
performed. trajectory revealing the progression from non-malignant to
malignant and finally metastatic cells (Fig. 1H). The C3 cluster
was positioned at the upper right corner in the trajectory curve,
Single-cell RNA-seq data analysis
indicating as a clear starting point of the trajectory, and the
The single-cell libraries were prepared using the Chromium Single Cell
Gene Expression Solution, Chromium Single Cell 5’ Gel Bead, Chip, and developmentalroutewasdeterminedtostartfromtheinitialstate
Library Kits v2 (10X Genomics) and cells were loaded at a density of andthenbifurcateintometastasis-relatedcellfate1or2.SinceC2
8000–10,000 cells per channel to ensure optimal recovery. Cells were clusterandC9clusterwererespectivelylocatedatoneendofthe
partitioned into gel beads in the Chromium device for mRNA barcoded trajectorycurveexhibitingrelativelyhigherCNVlevels(Fig.1G,H),
reversetranscriptionand cell lysis, followed by amplification, fragmenta- thesetwosub-clusterswerethussuggestedtobeassociatedwith
tion,5’adapteradditionandsampleindexing.Forcell-cellcommunication
GCmetastasis.Subsequently,Kaplan-Meiersurvivalanalysisofthe
analysis, the R package “CellChat” (v1.4.0) was used to calculate and
representativegenesfromC2clusterandC9clustershowedthat
visualize cell communication networks. The KOBAS 3.0 and GOseq R
higher expression levels of the representative genes from C2
packages were used for Kyoto Encyclopedia of Genes and Genomes
cluster were related to higher survival rates in GC patients, while
(KEGG) and Gene Ontology (GO) enrichment analysis of differentially
expressed genes (DEGs). For regulatory networks analysis, the pySCENIC higher expression levels of the representative genes from C9
(v0.12.0)wasused,withtheScanpy.AnnDataobjectfromepithelialtissue cluster were related to lower survival rates (Figure S2 and S3).
readcountsusedtocalculatetranscriptionfactoractivity.Cellclusterswere SNAP25,agenespecificallyenrichedinC9cluster,wasselectedas
used as input, and the AUC matrix was generated using default a biomarker for C9 cluster. Dual immunofluorescence staining of
parameters,withtheregulatoryspecificityscores(RSS)usedforpredicting 36 pairs of metastatic lymph nodes and paired primary gastric
foreachcellcluster. tumors revealed that PanCK+ SNAP25+ expression was higher in
the metastatic lymph nodes than that in the primary tumors
Statistical analysis (Fig. 1I). In summary, these data indicated that the malignant C9
GraphPadPrism8.0wasusedforstatisticalanalysis.Differencesbetween cluster was significantly associated with GC metastasis and
groupswereassessedusingtwo-tailedunpairedt-testsorMann-Whitney attracted moreattention for further study.
tests according to the results of normal distribution analysis, while
differencesamongthreeormoregroupswereanalyzedthroughone-way EGR4wasupregulated andpositively associated withGC
ANOVA method followed by Tukey’s post hoc test. The survival curves
metastasis
wereplottedusingtheKaplan-Meiermethodandcomparedby thelog-
We used the single-cell regulatory network inference and
ranktest.CategoricaldatawerecomparedusingFisher’sexacttestorchi-
clustering(SCENIC)methodtoidentifykeyregulatorsinC9cluster
square test. All experiments, except for those involving mice, were
performed in at least three independent biological replicates, with by linking cis-regulatory sequence information with scRNA-seq
technical replicates for each experiment. P<0.05 was considered data. SCENIC analysis showed that EGR4, NEUROD1 and
statisticallysignificant. NEUROD2showedthehighestregulatoryactivityinC9thecluster
(Fig. 2A). Kaplan-Meier survival analysis revealed that higher
NEUROD1 and NEUROD2 levels were associated with higher
RESULTS survivalratesinGCpatients(FigureS4).However,analysisofEGR4
IdentificationofcancercellclustersenrichedinGCmetastasis expression in GC patients through TCGA data sets and paired
To comprehensively clarify and understand the cell subsets that para-cancerousandtumortissuesshowedthatitwasupregulated
mayplayanimportantroleinGCmetastasis,wecollectedsixpairs inGCsamples(Fig.2B,C),anddualimmunofluorescencestaining
ofprimarygastrictumorsandpaired metastaticlymphnodesfor also demonstrated that PanCK+ EGR4+ expression was higher in
scRNA-seq (by 10x Genomics). All lymph node samples were the metastatic lymph nodes than that in the primary tumors
confirmed as metastatic by H&E staining of slides and the (Fig. 2D). Furthermore, Kaplan-Meier survival analysis indicated
confirmationofthreepathologists.Afterfilteringoutthedamaged that higher EGR4 expression was associated with lower patient
ordeadcellsandpotentialdoublets,asingle-cellatlasconsisting survival rates (Fig. 2E–G). These results indicate that EGR4 can
of59,918cells wasconstructed (Fig. 1A).Usinguniformmanifold serve as a prognosis biomarker for GC metastasis. Subsequently,
approximation and projection (UMAP), we generated a two- weconstructedEGR4overexpressionandknockdownGCcelllines
dimensionalmapwith19clustersacross 12samples (FigureS1A, using lentivirus (Fig. 2H, I), and found that EGR4 overexpression
B). These clusters were annotated into eight cell types, including upregulated the expression of representative genes of the C9
epithelialcells(EPCAM,KRT18,GKN1asmarkers),fibroblasts(DCN, cluster,includingNPAS3,PALLD,CHGA,RIMS2,KCNB2,GHRLand
COL1A1,COL1A2asmarkers),plasmaBcells(MZB1,IGHA2,SDC1 SNAP25(Fig.2J,K).ThesedataindicatethatEGR4ingastriccancer
as markers), myeloid cells (S100A9, S100A8, TREM1 as markers), epitheliummaybeakeyregulatoroftheC9cluster;Therefore,we
natural killer (NK) cells (KLRD1, NKG7, GNLY as markers), namedtheC9cancercellsubpopulationastheEGR4+cancercell
endothelial cells (VWF, ENG, FLT1 as markers), T cells (CD3D, subpopulation.
CD3E, CD2 as markers), and B cells (MS4A1, CD79A, IGHD as
markers)(Fig. 1Cand S1C). EGR4promoted GC cellmigration, invasion andmetastasis
GiventhatGCcellsoriginatefromepithelialcells,unsupervised To verify the function of EGR4 in GC metastasis, we performed a
clustering analysis on the UMAP were performed and the seriesofinvitroandinvivoexperiments.Transwellmigrationand
epithelial cells was re-clustered into 10 distinct clusters (Fig. 1D), invasion assays revealed that EGR4 overexpression dramatically
with the expression of the top cluster-specific genes shown in promotedGCcellmigrationandinvasion(Fig.3A,B),whileEGR4
Fig.1E.Todistinguishthemalignantclustersfromnon-malignant knockdowndramaticallyinhibitedGCcellmigrationandinvasion
clusters, we assessed the copy number variation (CNV) levels of (Fig. 3C, D). More importantly, in nude mice tail vein-lung
each epithelial cell cluster, revealing that epithelial cells in the metastasis model, we found that EGR4 overexpression
CellDeathandDisease (2025) 16:807

## Page 4

W.Liuetal.
4
Fig.1 IdentificationofcancercellclustersenrichedinGCmetastasis.APipelineofthescRNA-seqstudydesign.BUMAPvisualizationof
59,918 cells color-coded by major cell types. C Bubble plots showing expression of marker genes across the major cell types. D UMAP of
epithelialcellsrevealing10distinctclusters.EHeatmapofthetopmarkergenesineachepithelialsub-cluster.FCNVanalysisinepithelialcells
from primary tumors and lymph nodes. G CNV analysis in epithelial sub-clusters. H Trajectory analysis showing two distinct cell fates for
epithelialcells.IImmunofluorescencestainingandquantitativeanalysisofPanCK+SNAP25+cellsinsectionsofpairedprimarytumorand
lymphnodemetastasis.Foreachtissuesection,threerandomlyselectedfieldsofview(FOVs)wereanalyzed,andthepositivityrateofSNAP25
inPanCK-positiveepithelialcellswascalculatedforeachFOV,withtheaveragevaluerepresentingtheSNAP25expressionlevelpersample.
**p<0.01bypairedt-test.*p<0.05;**p<0.01;***p<0.001.
CellDeathandDisease (2025) 16:807

## Page 5

W.Liuetal.
5
Fig.2 EGR4wasupregulatedandpositivelyassociatedwithGCmetastasis.ADotplotsshowingregulonactivitiesindifferentepithelialcell
sub-clusters.BEGR4mRNAexpressionintheTCGA-GCdataset.CEGR4mRNAexpressioninpairedpara-cancerousandtumortissuesfromGC
patients.DImmunofluorescencestainingandquantitativeanalysisofPanCK+EGR4+cellsinsectionsofpairedprimarytumorandlymphnode
metastasis.Foreachtissuesection,threerandomlyselectedFOVswereanalyzed,andthepositivityrateofEGR4inPanCK-positiveepithelial
cellswascalculatedforeachFOV,withtheaveragevaluerepresentingtheEGR4expressionlevelpersample.***p<0.001bypairedt-test.E–G
Kaplan-Meier survival analysis of GC patients based on EGR4 expression levels. H, I Western blot and RT-qPCR validation of EGR4
overexpression andknockdown inGC cells. J, KRT-qPCRanalysis ofexpression of C9 marker genes upon EGR4over-expression. *p<0.05,
**p<0.01,***p<0.001.
CellDeathandDisease (2025) 16:807

## Page 6

W.Liuetal.
6
Fig. 3 EGR4 promoted GC cell migration, invasion and metastasis. A, B Transwell assays showed the effect of EGR4 over-expression on
migrationandinvasionofHGC27andMKN45cells.C,DTranswellassaysshowedtheeffectofEGR4knockdownonmigrationandinvasionof
HGC27andMKN45cells.EH&Estainingoflungmetastaticlesionsintheinvivolungmetastasismicemodel.F,GQuantitativeanalysisofthe
numberofmetastasesandpercentageofmetastasislociintheinvivolungmetastasismicemodel.*p<0.05,**p<0.01,***p<0.001.
significantly enhanced tumor cell colonization in the lungs signaling, Ras signaling, MAPK signaling and PI3K-Akt signaling
(Fig. 3E–G). These results confirmed that EGR4 played a pivotal pathways(Fig.4C).Ontheotherhand,RNA-seqanalysisofEGR4-
rolein promotingGC metastasis. overexpressing cells revealed the differentially expressed genes
(Fig.4D),withGeneOntology(GO)analysishighlightingimmune
EGR4transcriptionally upregulated GDF15expression in response and extracellular secretion pathways (Fig. 4E). By cross-
GCcells referencing the ChIP-seq and RNA-seq data, we identified 11
We hypothesized that the potential mechanism by which EGR4 overlapping genes, including GDF15, which showed the highest
promotedGCmetastasismaydependonitsdirectgenetargetsas upregulation in the immune response and extracellular secretion
atranscriptionfactor.ToidentifythedirectgenetargetsofEGR4, pathway (Fig. 4F). Growth/differentiation factor 15 (GDF15), also
weperformedChIP-seqandRNA-seq.Notably,EGR4bindingsites known as macrophage inhibitory cytokine-1 (MIC1) and nonster-
weresignificantly enrichedaround transcriptional start sites(TSS, oidal anti-inflammatory drug-activated gene-1 (NAG-1), is con-
−3kb to +3kb) (Fig. 4A). Genomic annotation of peaks revealed sideredasacachexiafactorandhasbeenusedasabiomarkerfor
their distribution across various genomic elements (Fig. 4B). tumor diagnosis and prognosis [23–29]. Genomic distribution of
Moreover, Kyoto Encyclopedia of Genes and Genomes (KEGG) the EGR4 enriched peaks revealed their location on GDF15
pathway analysis identified significant enrichment in ErbB promoter region containing conserved recognition sequence of
CellDeathandDisease (2025) 16:807

## Page 7

W.Liuetal.
7
EGR4 (Fig. 4G, H). ChIP-qPCR experiments demonstrated signifi- binding site exhibited dramatically reduced luciferase activity
cantenrichmentofDNAfragmentsattheGDF15promoterregion compared to the wild-type (WT) reporter (Fig. 4J), indicating that
in EGR4 antibody-immunoprecipitated DNA-protein complexes EGR4 can activate GDF15 transcription by direct binding to the
(Fig. 4I). We performed a promoter luciferase reporter assay to motif. Western blot and ELISA assay further validated that EGR4
investigatewhetherEGR4bindingtotheGDF15promoter region upregulated GDF15 expression and secretion (Fig. 4K, L). In
enhanced GDF15 transcriptional activity, and the results showed addition, immunofluorescence staining showed higher GDF15
that the mutant (MUT) luciferase reporter with a mutated EGR4 expressiononPanCK+EGR4+cellsinthemetastaticlymphnodes
CellDeathandDisease (2025) 16:807

## Page 8

W.Liuetal.
8
Fig.4 EGR4transcriptionallyupregulatedGDF15expressioninGCcells.A,BDistributionofEGR4bindingpeaksneartranscriptionstart
sites(TSS)andgenestructures.CKEGGpathwayenrichmentanalysisoftheEGR4targetgenes.DVolcanoplotofEGR4-regulatedgenesby
RNA-seq.EGOanalysisofEGR4-regulatedgenesbyRNA-seq.FVenndiagramintegratingChIP-seqandRNA-seqdatatoidentifydirecttarget
andeffectorgenesofEGR4,includingGDF15.GDiagramshowingthedistributionofEGR4bindingpeaksnearTSSofGDF15genebyChIP-seq.
HDiagramshowingtheconservedrecognition sequenceofEGR4inGDF15promoter region.IChIP-qPCRconfirmingEGR4binding tothe
GDF15promoter.JLuciferasereportergeneassayconfirmingEGR4activatingthetranscriptionalactivityofGDF15promoter.K,LWesternblot
andELISAassaysconfirmingtheupregulationofGDF15expressionbyEGR4.MImmunofluorescencestainingofEGR4andGDF15expression
in PanCK+ cells in paired primary tumor and lymph node metastasis sections from 36 GC patients. N Quantitative analysis of the GDF15
expressioninPanCK+cells.Foreachtissuesection,threerandomlyselectedFOVswereanalyzed,andthepositivityrateofGDF15inPanCK-
positive epithelial cells was calculated for each FOV, with the average value representing the GDF15 expression level per sample.
***p<0.001bypairedt-test.OCorrelationbetweenEGR4andGDF15expressioninPanCK+cells.Foreachtissuesection,threerandomlyFOVs
wereanalyzed,andthepositivityrateofEGR4orGDF15inPanCK-positiveepithelialcellswascalculatedforeachFOV,withtheaveragevalue
representingtheEGR4orGDF15expressionlevelpersample,respectively.***p<0.001byPearson’scorrelationanalysis.*p<0.05,**p<0.01;
***p<0.001.
than that in primary tumors, with a positive correlation between EGR4+GCcells activated CAFs through GDF15to promote
GDF15andEGR4expression(Fig.4M,N).Theseresultsconfirmed ECMremodeling andGC cellmotility
thatGDF15 was adirect target of EGR4in GCcells. ToidentifypotentialinteractionsbetweenEGR4+GCcellsandTME
cells, we performed CellChat analysis to map intercellular
EGR4activatedErbB3/ErbB1anddownstreamMAPK/ERKand signaling. The results showed that EGR4+ GC cells revealed more
PI3K/AKT signaling viaGDF15 and stronger interactions with CAFs (Fig. 6A, B). Through the
Based on GO analysis of ChIP-seq data, we found that EGR4 was analysis of TIMER2.0 database, it was found that the survival of
significantly associated with pathways such as ErbB signaling and patientswithhighexpressionofEGR4andincreasedinfiltrationof
Ras signaling, MAPK signaling, PI3K-Akt signaling, which could be CAFs in GC was significantly shortened (Figure S6A). Since the
downstream of ErbB signaling [30]. Therefore, we further investi- complexityofCAFs,weperformedunsupervisedUMAPclustering
gated whether EGR4 activated the MAPK/ERK and PI3K/AKT analysis and clustered CAFs into four groups (Fig. 6C). Based on
signaling pathways in GC cells through GDF15. Western blot GO analysis, these clusters were associated with antigen
confirmed that EGR4 activated the MAPK/ERK and PI3K/AKT presentation, extracellular matrix, inflammatory response, and
signaling pathways and Epithelial-Mesenchymal Transition (EMT), a smooth muscle cell-like characteristics, and were thus named
key characteristic of metastatic cells (Fig. 5A). Immunostaining of apCAF (antigen-presenting CAF), eCAF (extracellular matrix-
tissuesectionsfrommicealsoshowedthatoverexpressionofEGR4 producing CAF), iCAF (inflammatory CAF), and mCAF (myofibro-
upregulated the level of GDF15, p-PI3K and p-ERK, whereas blastic CAF), respectively (Fig. 6D). Subsequent CellChat analysis
knocking down EGR4 decreased the level of GDF15, p-PI3K and revealed that EGR4+ GC cells showed more and stronger
p-ERK(Fig.5BandFigureS5).Besides,wetransfectedGCcellswith interactions with eCAFs than other CAF clusters (Fig. 6E, F).
siRNA targeting GDF15, and the results indicated that knocking Immunofluorescencestainingonpairsofmetastaticlymphnodes
down GDF15 would impair the activation of the PI3K/AKT and and primary tumors from 36 GC patients showed that the
MAPK/ERK signaling pathways and EMT in EGR4-overexpressing expressionofeCAFmarkersMMP9,COL1A1,andFibronectinwas
gGC cells (Fig. 5C). Additionally, transwell assays revealed that significantly higher in metastatic lymph nodes than in primary
knockdownof GDF15 significantly reduced migration and invasion tumors,whichwaspositivelycorrelatedwithEGR4level(Fig.6G–I).
of EGR4-overexpressing GC cells (Fig. 5D, E). These results indicate TheseresultssuggestthattheEGR4+GCcellsclustermaypromote
that EGR4 may activate the MAPK/ERK and PI3K/AKT signaling ECM remodeling through interaction and activation of eCAFs to
pathwaysthroughGDF15,therebypromotingGCcellmotility. facilitate metastasis.
To explore the specific mechanism by which GDF15 activated To further validate the effect of EGR4+ GC cells on eCAFs
theMAPK/ERKandPI3K/AKTpathways,weperformedanti-GDF15 activation, we co-cultured control and EGR4-overexpressing GC
co-IP/mass spectrometry and found that GDF15 could bind to cellswithhumanprimarygastriccancer-associatedfibroblastsfor
ErbB3(Fig.5F),whichwasvalidatedbyco-IP/WB(Fig.5G).Studies 24hours. QPCR experiments showed that co-incubation of EGR4-
have shown that ErbB3 can form heterodimers with ErbB1 and overexpressing GC cells upregulated genes related to matrix
activate downstream MAPK/ERK and PI3K/AKT signaling path- remodeling, such as MMP2, COL1A1 and Fibronectin in CAFs,
ways [30–32]. Additionally, GDF15 promotes ErbB1 signal comparedtothoseincubatedwithcontrolGCcells(Fig.7A),which
transduction and its tyrosine phosphorylation [33, 34]. Through was abolished when GDF15 was knocked down through siRNA
immunoprecipitation experiments, we found that rhGDF15 (Fig. 7B), suggesting that EGR4+GC cells promoted eCAFs
treatment on GC cells promoted the binding of ErbB3 to ErbB1 activation through GDF15. In addition, TIMER2.0 data analysis
and upregulated the level of ErbB1 phosphorylation (Fig. 5H). showed that high expression of GDF15 or EGR4+GDF15+ and
Besides, immunoprecipitation experiments also revealed that increased CAFs infiltration in gastric cancer patients had a
GDF15 can bind to ErbB1 (Fig. 5I). These suggested that GDF15 significantly shorter survival time (Figure S6B, C). The TGF-β
can bind and activate ErbB1 through ErbB3 binding and the pathwayisacorepathwayforCAFactivationandECMremodeling
formation of ErbB3-ErbB1heterodimer. To verify whether GDF15 [35–37], and GDF15 could bind to the TGF-β receptor and
activated downstream signaling pathways through ErbB1 activa- activatesdownstreamSmad2/3pathway[38–40].Totestwhether
tion, we used transwell assays to examine the effect of ErbB1 GDF15 promote matrix remodeling through TGF-β receptor, we
inhibitor Erlotinib on the migration and invasion of rhGDF15- treated CAFs with rhGDF15 for 24h, and found that rhGDF15
treated GC cells. The results showed that rhGDF15 promoted promotedtheCAFs-mediatedmatrixremodelingprocess.Besides,
migration and invasion of GC cells, which was inhibited upon TGF-β receptor inhibitor SB525334 treatment significantly
Erlotinib treatment (Fig. 5J, K). These results indicate that EGR4 impaired the promotion effect of rhGDF15 on matrix remodeling
could promote the formation of ErbB3-ErbB1 heterodimers (Fig. 7C). In addition, transwell invasion assay indicated that co-
through GDF15 to activate the ErbB signaling and downstream culture with CAFs could promote the invasion of GC cells, which
MAPK/ERKandPI3K/AKTsignalingpathwaysandpromoteGCcell was significantly enhanced in GC cells overexpressing EGR4
motility. (Fig. 7D). Furthermore, rhGDF15 treatment enhanced the
CellDeathandDisease (2025) 16:807

## Page 9

W.Liuetal.
9
Fig.5 EGR4activatedErbB3/ErbB1signalinganddownstreamMAPK/ERKandPI3K/AKTviaGDF15.AWesternblotshowingtheeffectof
EGR4ontheexpressionoftheproteinsofMAPK/ERKandPI3K/AKTsignalingandEMTmarkersinGCcells.BTheimmunofluorescenceimages
show the co-localization of EGR4, GDF15, p-PI3K and p-ERK in the nude mouse model. C Western blot showing the effect of GDF15
knockdown on the expression of the proteins of MAPK/ERK and PI3K/AKT signaling and EMT markers in EGR4-overexpressing GC cells.
D,ETranswellassaysshowingtheeffectofGDF15knockdownonthemigrationandinvasionofEGR4-overexpressingGCcells.FSchematic
diagramofMassspectrometryanalysisofGDF15interactorsandtherepresentativepeptidemassspectrometrypeaksofErbB3inGDF15co-IP
complex.GCo-IP/westernblotshowingthebindingofGDF15andErbB3.HCo-IP/westernblotshowingtheeffectofrhGDF15treatmenton
the binding of ErbB3 with ErbB1 and the phosphorylation of ErbB1. I Co-IP/western blot showing the binding of GDF15 and ErbB1.
J,KTranswellassayshowingtheinhibitoryeffectofErlotinib(10µmol/l)onthemigrationandinvasionofrhGDF15(200ng/ml)stimulatedGC
cells.*p<0.05,**p<0.01,***p<0.001.
CellDeathandDisease (2025) 16:807

## Page 10

W.Liuetal.
10
Fig.6 InteractionbetweenEGR4+GCcellsandCAFs.A,BHeatmapsofinteractionsbetweenEGR4+GCcellsandTMEcells.CUMAPofCAFs
showing4clusters.DGOanalysisofthe4differentCAFsubtypes.E,FHeatmapsofinteractionsbetweenEGR4+GCcellsandCAFsubtypes.
G–IImmunofluorescencestainingofECMmarkergenesinCAFsandcorrelationanalysiswithEGR4insectionsofpairedprimarytumorand
lymphnodemetastasis.FAP,fibroblastactivationprotein.Foreachtissuesection,threerandomlyFOVswereanalyzed,andthepositivityrate
of MMP9, COL1A1 or FN1 in FAP-positive CAFs and that of EGR4 in PanCK-positive epithelial cells was calculated for each FOV, with the
averagevaluerepresentingtheMMP9,COL1A1,FN1orEGR4expressionlevelpersample.Thepairedt-testandPearsoncorrelationanalysis
wereusedforanalysis.*p<0.05,**p<0.01,***p<0.001.
CellDeathandDisease (2025) 16:807

## Page 11

W.Liuetal.
11
Fig.7 EGR4-upregulatedGDF15inGCcellsactivatedCAFstopromoteECMremodelingandGCcellmotility.ART-qPCRdetectionofECM
remodelinggenesinCAFsco-culturedwithEGR4over-expressingorcontrolGCcells.BRT-qPCRdetectionofECMremodelinggenesinCAFs
co-culturedwithEGR4over-expressingGCcellsuponGDF15knockdown.CRT-qPCRdetectionofECMremodelinggenesinCAFstreatedwith
rhGDF15(200ng/ml)upontreatmentofTGFβRinhibitorSB525334(5µM).DThetranswellassaydemonstratedthepromotioneffectofCAFs
on the invasion of GC cells. The invaded GC cells were counted, which exhibited significantly smaller cell volumes than the CAFs. E The
transwellassaydemonstratedtheroleofrhGDF15(200ng/ml)treatmentonthepromotioneffectofCAFsontheinvasionofGCcells.The
invadedGCcellswerecounted,whichexhibitedsignificantlysmallercellvolumesthantheCAFs.*p<0.05,**p<0.01,***p<0.001.
promotion effect of CAFs on the invasion of co-cultured GC cells DISCUSSION
(Fig.7E).TheseresultssuggestthatGDF15secretedbyEGR4+GC Gastric cancer (GC) is a highly heterogeneous malignant tumor,
cellscouldactivateCAF-mediatedmatrixremodelingthroughthe anddespitethewidespreadapplicationofscRNA-seqinresolving
TGF-βpathway topromote cellmotility. itsheterogeneity,thecriticaltumorcellsubpopulationsdrivingGC
CellDeathandDisease (2025) 16:807

## Page 12

W.Liuetal.
12
metastasis and their underlying molecular mechanisms remain 4. Smyth EC, Nilsson M, Grabsch HI, van Grieken NC, Lordick F. Gastric cancer.
poorlyunderstood[41,42].Inthisstudy,weemployedscRNA-seq Lancet.2020;396:635–48.
toanalyzethemetastaticlymphnodesandpairedprimarytumors 5. JanjigianYY,ShitaraK,MoehlerM,GarridoM,SalmanP,ShenL,etal.First-line
fromGCpatients,leadingtotheidentificationofanEGR4+cancer nivolumabpluschemotherapyversuschemotherapyaloneforadvancedgastric,
cell subpopulation strongly associated with GC metastasis. This gastro-oesophageal junction, and oesophageal adenocarcinoma (CheckMate
649):arandomised,open-label,phase3trial.Lancet.2021;398:27–40.
subpopulation was demonstrated to play a pivotal role in
6. RostamiM,KzarMH,AbdAZ,KadhimRA,HamoodSA,AbdulwahidAS,etal.The
metastasis, highlighting itsclinical relevance.
roleoflymphnodemetastasisinearlygastritisIndividualsfollowingnoncurative
Our findings demonstrate that EGR4 directly binds to the
endoscopicResection:asystematicreviewandmeta-analysis.JAyubMedColl
promoterregionofGDF15,upregulatingitsexpression.GDF15,in Abbottabad.2023;35:658–63.
turn, interacts with ErbB3, enhancing the interaction between 7. LawsonDA,Kessenbrock K,DavisRT,Pervolarakis N,WerbZ.Tumourhetero-
ErbB3 and ErbB1 and activating the ErbB1 signaling pathway. geneityandmetastasisatsingle-cellresolution.NatCellBiol.2018;20:1349–60.
ErbB1inhibitorErlotinibeffectivelysuppressedthemigrationand 8. StuartT,SatijaR.Integrativesingle-cellanalysis.NatRevGenet.2019;20:257–72.
invasion of rhGDF15-treated GC cells. These results suggest that 9. PapalexiE,SatijaR.Single-cellRNAsequencingtoexploreimmunecellhetero-
theGDF15-ErbB3/ErbB1axismaybeapotentialtherapeutictarget
geneity.NatRevImmunol.2018;18:35–45.
10. KataiH,IshikawaT,AkazawaK,IsobeY,MiyashiroI,OdaI,etal.Five-yearsurvival
for intervening GC metastasis. However, the precise mechanism
analysis of surgically resected gastric cancer cases in Japan: a retrospective
by which GDF15 enhances the interaction between ErbB3 and
analysis of more than 100,000 patients from the nationwide registry of the
ErbB1remainstobeelucidatedandwarrantsfurtherinvestigation. JapaneseGastricCancerAssociation(2001-2007).GastricCancer.2018;21:144–54.
Additionally, we uncover that GDF15 promotes metastasis by 11. LehnertT,ErlandsonRA,DecosseJJ.Lymphandbloodcapillariesofthehuman
activating the TGF-β signaling pathway in ECM-producing eCAFs. gastricmucosa.AmorphologicbasismetastasisearlygastriccarcinomaGastro-
This activation induces eCAFs to secrete ECM components (e.g., enterol.1985;89:939–50.
collagen, fibronectin) and proteases (e.g., matrix metalloprotei- 12. Alexander JS, Ganta VC, Jordan PA, Witte MH. Gastrointestinal lymphatics in
nases, MMPs), which remodel the TME into a “stiffened” matrix. healthanddisease.Pathophysiology.2010;17:315–35.
This remodeling provides physical support for cancer cells and 13. Hogarth CA, Mitchell D, Small C, Griswold M. EGR4 displays both a cell- and
intracellular-specific localization pattern in the developing murine testis. Dev
activates mechanosensitive pathways such as YAP/TAZ, thereby
Dyn.2010;239:3106–14.
enhancing cancer cell migration and invasion [43]. Furthermore,
14. DiPersioS,TekathT,Siebert-KussLM,CremersJF,WistubaJ,LiX,etal.Single-cell
eCAF-derivedgrowthfactors(e.g.,TGF-β,VEGF)induceepithelial-
RNA-sequnravelsalterationsofthehumanspermatogonialstemcellcompart-
mesenchymal transition to further facilitate metastasis [44, 45]. mentinpatientswithimpairedspermatogenesis.CellRepMed.2021;2:100395.
Given the diversity of GDF15 receptors and their expression 15. O’Donovan KJ, Tourtellotte WG, Millbrandt J, Baraban JM. The EGR family of
patterns,futurestudiesshouldexploretheroleoftheEGR4/GDF15 transcription-regulatoryfactors:progressattheinterfaceofmolecularandsys-
axisin immuneregulation duringGC metastasis. temsneuroscience.TrendsNeurosci.1999;22:167–73.
Our findings have significant translational implications for the 16. PoirierR,ChevalH,MailhesC,GarelS,CharnayP,DavisS,etal.Distinctfunctions
precision treatment of GC metastasis. Targeting the EGR4/GDF15
ofegrgenefamilymembersincognitiveprocesses.FrontNeurosci.2008;2:47–55.
17. KnapskaE,KaczmarekL.Ageneforneuronalplasticityinthemammalianbrain:
axis may offer a novel therapeutic strategy. For instance, the
development of small-molecule inhibitors specifically targeting
Zif268/Egr-1/NGFI-A/Krox-24/TIS8/ZENK?.ProgNeurobiol.2004;74:183–211.
18. Matsuo T, Dat LT, Komatsu M, Yoshimaru T, Daizumoto K, Sone S, et al. Early
EGR4 could suppress GDF15 expression and inhibit metastasis.
growthresponse4isinvolvedincellproliferationofsmallcelllungcancerthrough
Neutralizing antibodies against GDF15 or soluble ErbB3 receptor transcriptionalactivationofitsdownstreamgenes.PLoSOne.2014;9:e113606.
trapscouldblocktheinteractionbetweenGDF15andErbB3[46], 19. HeS,LinJ,XuY,LinL,FengJ.ApositivefeedbackloopbetweenZNF205-AS1and
effectively inhibit the metastatic potential of EGR4+ GC cells. EGR4 promotes non-small cell lung cancer growth. Journal Cell Mol Med.
Additionally, TGF-β receptor inhibitors (e.g., SB525334) and MMP 2019;23:1495–508.
inhibitors(e.g.,Marimastat)couldattenuateGDF15-inducedeCAF 20. GongX,ZouL,WangM,ZhangY,PengS,ZhongM,etal.Gramicidininhibits
activation,therebyreducingthesupportiveroleoftheTMEinGC cholangiocarcinomacellgrowthbysuppressingEGR4.ArtifCellsNanomedBio-
technol.2020;48:53–59.
metastasis.CombinationtherapiesinvolvingErbB1inhibitors(e.g.,
21. PuramSV,Tirosh I,ParikhAS,PatelAP,YizhakK,GillespieS,etal.Single-Cell
Erlotinib) and GDF15-neutralizing antibodies may also yield
Transcriptomic Analysisof Primary and Metastatic TumorEcosystems in Head
synergistic effects. andNeckCancer.Cell.2017;171:1611–24.e24.
In conclusion, the present study identifies the EGR4+GC cell 22. LiuYM,GeJY,ChenYF,LiuT,ChenL,LiuCC,etal.CombinedSingle-Celland
subpopulationasacriticaldriverofGCmetastasisandelucidates SpatialTranscriptomicsRevealtheMetabolicEvolvementofBreastCancerduring
the molecular mechanisms by which the EGR4/GDF15 axis EarlyDissemination.AdvSci(Weinh).2023;10:e2205395.
promotes GC metastasis through the activation of the ErbB3/ 23. Al-SawafO,WeissJ,SkrzypskiM,LamJM,KarasakiT,ZambranaF,etal.Bodycom-
ErbB1 signaling and eCAF-mediated ECM remodeling. These positionandlungcancer-associatedcachexiainTRACERx.NatMed.2023;29:846–58.
findings not only provide new insights into the molecular 24. Kim-Muller JY, Song L, LaCarubba PB, Pashos E, Li X, Rinaldi A, et al. GDF15
neutralization restores muscle function and physical performance in a mouse
mechanisms underlying GC metastasis but also lay the ground-
modelofcancercachexia.CellRep.2023;42:111947.
workforthedevelopmentoftargetedtherapiesagainsttheEGR4/
25. SuribenR,ChenM,HigbeeJ,OeffingerJ,VenturaR,LiB,etal.Antibody-mediated
GDF15axis.
inhibitionofGDF15-GFRALactivityreversescancercachexiainmice.NatMed.
2020;26:1264–70.
26. LiC,WangX,CasalI,WangJ,LiP,ZhangW,etal.Growthdifferentiationfactor15
DATAAVAILABILITY isapromisingdiagnosticandprognosticbiomarkerincolorectalcancer.JCell
AllrawdataareintheGenomeSequenceArchiveforHuman(GSA-Human)atthe MolMed.2016;20:1420–6.
National Genomics Data Center under the accession number HRA009590 (http:// 27. MaJ,TangX,SunWW,LiuY,TanYR,MaHL,etal.MutantGDF15presentsapoor
bigd.big.ac.cn/gsa-human). prognosticoutcomeforpatientswithoralsquamouscellcarcinoma.Oncotarget.
2016;7:2113–22.
28. MulderFI,BoschF,CarrierM,MallickR,MiddeldorpS,vanEsN,etal.Growth
REFERENCES differentiationfactor-15forpredictionofbleedingincancerpatients.JThromb
1. SungH,FerlayJ,SiegelRL,LaversanneM,SoerjomataramI,JemalA,etal.Global Haemost.2022;20:138–44.
CancerStatistics2020:GLOBOCANEstimatesofIncidenceandMortalityWorld- 29. ZhaoJ,LiY,HuangY,SuP,NieF,YangP,etal.Tumor-DerivedGDF15Induces
widefor36Cancersin185Countries.CACancerJClin.2021;71:209–49. TumorAssociatedFibroblastTransformationFromBMSCsandFibroblastsinOral
2. ThriftAP,WenkerTN,El-SeragHB.Globalburdenofgastriccancer:epidemiological SquamousCellCarcinoma.JCellPhysiol.2025;240:e31498.
trends,riskfactors,screeningandprevention.NatRevClinOncol.2023;20:338–49. 30. SerginaNV,RauschM,WangD,BlairJ,HannB,ShokatKM,etal.EscapefromHER-
3. EusebiLH,TeleseA,MarascoG,BazzoliF,ZagariRM.Gastriccancerprevention family tyrosine kinase inhibitor therapy by the kinase-inactive HER3. Nature.
strategies:Aglobalperspective.JGastroenterolHepatol.2020;35:1495–502. 2007;445:437–41.
CellDeathandDisease (2025) 16:807

## Page 13

W.Liuetal.
13
31. EngelmanJA,ZejnullahuK,MitsudomiT,SongY,HylandC,ParkJO,etal.MET Projects in Guangdong Province(2021B0101420005); the National Natural Science
amplification leads to gefitinib resistance in lung cancer by activating FoundationofChina(QLZ,82173033;YWX,82102712);ChinaPostdoctoralScience
ERBB3signaling.Science.2007;316:1039–43. Foundation(YWX,2021M690751);GuangdongProvincialKeyLaboratoryofArtificial
32. SchoeberlB,PaceEA,FitzgeraldJB,HarmsBD,XuL,NieL,etal.Therapeutically Intelligence in Medical Image Analysis and Application (2022B1212010011). The
targetingErbB3:akeynodeinligand-inducedactivationoftheErbBreceptor- figuresweredrawnbyFigdraw.
PI3Kaxis.SciSignal.2009;2:ra31.
33. Carrillo-GarciaC,ProchnowS,SimeonovaIK,StrelauJ,Holzl-WenigG,MandlC,
etal.Growth/differentiationfactor15promotesEGFRsignalling,andregulates AUTHORCONTRIBUTIONS
proliferation and migration in the hippocampusofneonatal and young adult
QZ designed the study and prepared the manuscript. WL and YL performed
mice.Development.2014;141:773–83.
experiments.YL,LL,andWLperformedthestatisticalanalyses.LZ,ZL,RZ,andCZ
34. KimK,LeeJJ,YangY,YouK,LeeJ.Macrophageinhibitorycytokine-1activates assistedwithtissuesamplecollection.WFandLLperformedthedataanalysisand
AKTandERK-1/2viathetransactivationofErbB2inhumanbreastandgastric interpretation.Allauthorsapprovedthefinalversionofthepaper.
cancercells.Carcinogenesis.2008;29:704–12.
35. CalonA,EspinetE,Palomo-PonceS,TaurielloDV,IglesiasM,CespedesMV,etal.
DependencyofcolorectalcanceronaTGF-beta-drivenprograminstromalcells
COMPETINGINTERESTS
formetastasisinitiation.CancerCell.2012;22:571–84.
Theauthorsdeclarenocompetinginterests.
36. BhowmickNA,ChytilA,PliethD,GorskaAE,DumontN,ShappellS,etal.TGF-beta
signalinginfibroblastsmodulatestheoncogenicpotentialofadjacentepithelia.
Science.2004;303:848–51.
37. OzdemirBC,Pentcheva-HoangT,CarstensJL,ZhengX,WuCC,SimpsonTR,etal. ETHICSAPPROVAL ANDCONSENT TOPARTICIPATE
Depletionofcarcinoma-associatedfibroblastsandfibrosisinducesimmunosup- This study has been approved by the Ethics Review Committee of Guangdong
pression and accelerates pancreas cancer with reduced survival. Cancer Cell. Provincial People’s Hospital Affiliated to Southern Medical University (approval
2014;25:719–34. number:KY2025-458-01).Alloperationswereconductedinaccordancewithrelevant
38. Li C, Wang J, Kong J, Tang J, Wu Y, Xu E, et al. GDF15 promotes EMT and guidelinesandregulations.Allparticipantshavesignedtheinformedconsentform.
metastasisincolorectalcancer.Oncotarget.2016;7:860–72.
39. Artz A, Butz S, Vestweber D. GDF-15 inhibits integrin activation and mouse
neutrophil recruitment through the ALK-5/TGF-betaRII heterodimer. Blood. ADDITIONAL INFORMATION
2016;128:529–41.
Supplementary information The online version contains supplementary material
40. XuJ,KimballTR,LorenzJN,BrownDA,BauskinAR,KlevitskyR,etal.GDF15/MIC-1
availableathttps://doi.org/10.1038/s41419-025-08095-w.
functions as a protective and antihypertrophic factor released from the myo-
cardiuminassociationwithSMADproteinactivation.CircRes.2006;98:342–50.
CorrespondenceandrequestsformaterialsshouldbeaddressedtoQinglingZhang.
41. Ren X, Kang B, Zhang Z. Understanding tumor ecosystems by single-cell
sequencing:promisesandlimitations.GenomeBiol.2018;19:211.
Reprints and permission information is available at http://www.nature.com/
42. ZhangM,HuS,MinM,NiY,LuZ,SunX,etal.Dissectingtranscriptionalhet-
reprints
erogeneityin primary gastricadenocarcinoma by singlecellRNAsequencing.
Gut.2021;70:464–75.
Publisher’snoteSpringerNatureremainsneutralwithregardtojurisdictionalclaims
43. Yoshida GJ. Regulation of heterogeneous cancer-associated fibroblasts: the inpublishedmapsandinstitutionalaffiliations.
molecular pathology of activated signaling pathways. J Exp Clin Cancer Res.
2020;39:112.
44. ChangYT,PengHY,HuCM,TienSC,ChenYI,JengYM,etal.Pancreaticcancer-
Open Access This article is licensed under a Creative Commons
derivedsmallextracellularvesicalezrinactivatesfibroblaststoexacerbatecancer
Attribution 4.0 International License, which permits use, sharing,
metastasis through STAT3 and YAP-1 signaling pathways. Mol Oncol.
adaptation,distributionandreproductioninanymediumorformat,aslongasyougive
2023;17:1628–47.
appropriatecredittotheoriginalauthor(s)andthesource,providealinktotheCreative
45. Zhang Z, Zhang Q, Wang Y. CAF-mediated tumor vascularization: From
Commonslicence,andindicateifchangesweremade.Theimagesorotherthirdparty
mechanisticinsightstotargetedtherapies.CellSignal.2025;132:111827. materialinthisarticleareincludedinthearticle’sCreativeCommonslicence,unless
46. MeleroI,deMiguelLM,deVelascoG,GarraldaE,Martin-LiberalJ,JoergerM,etal.
indicatedotherwiseinacreditlinetothematerial.Ifmaterialisnotincludedinthe
NeutralizingGDF-15canovercomeanti-PD-1andanti-PD-L1resistanceinsolid article’sCreativeCommonslicenceandyourintendeduseisnotpermittedbystatutory
tumours.Nature.2025;637:1218–27.
regulationorexceedsthepermitteduse,youwillneedtoobtainpermissiondirectly
from the copyright holder. To view a copy of this licence, visit http://
creativecommons.org/licenses/by/4.0/.
ACKNOWLEDGEMENTS
This project was supported by grants of High-level Hospital Construction Project
(XWBYKY-KF202204,QLZ,DFJHBF202108,andLSZ,KY012021425);KeyR&DProgram ©TheAuthor(s)2025
CellDeathandDisease (2025) 16:807