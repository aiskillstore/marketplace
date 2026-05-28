# Theoretical Foundations of scvi-tools

This document explains the mathematical and statistical principles behind scvi-tools.

## Core Concepts

### Variational Inference

**What is it?**
Variational Inference (VI) is a technique used to approximate complex probability distributions. In single-cell analysis, we want to understand the posterior distribution $p(z|x)$ — the probability of latent variables $z$ given the observed data $x$.

**Why use it?**
- Exact inference is computationally infeasible for complex models.
- It scales to large datasets (millions of cells).
- It provides uncertainty quantification.
- It enables Bayesian inference on cell states.

**How does it work?**
1. Define a simpler approximate distribution $q(z|x)$ with learnable parameters.
2. Minimize the KL divergence between $q(z|x)$ and the true posterior $p(z|x)$.
3. This is equivalent to maximizing the Evidence Lower Bound (ELBO).

**ELBO Objective Function**:
```
ELBO = E_q[log p(x|z)] - KL(q(z|x) || p(z))
       ↑                    ↑
Reconstruction term    Regularization term
```

- **Reconstruction term**: The model should generate data similar to the observations.
- **Regularization term**: The latent representation should conform to the prior distribution.

### Variational Autoencoders (VAEs)

**Architecture**:
```
x (Observed data)
    ↓
[Encoder Neural Network]
    ↓
z (Latent representation)
    ↓
[Decoder Neural Network]
    ↓
x̂ (Reconstructed data)
```

**Encoder**: Maps cells (x) to the latent space (z).
- Learns the approximate posterior distribution $q(z|x)$.
- Parameterized by a neural network with learnable weights.
- Outputs the mean and variance of the latent distribution.

**Decoder**: Maps the latent space (z) back to the gene space.
- Learns the likelihood $p(x|z)$.
- Generates gene expression values from the latent representation.
- Models count distributions (Negative Binomial, Zero-Inflated Negative Binomial).

**Reparameterization Trick**:
- Allows backpropagation through random sampling.
- Samples $z = \mu + \sigma \odot \epsilon$, where $\epsilon \sim N(0,1)$.
- Enables end-to-end training via gradient descent.

### Amortized Inference

**Concept**: Sharing encoder parameters across all cells.

**Traditional Inference**: Learning independent latent variables for each cell.
- Requires $n\_cells \times n\_latent$ parameters.
- Cannot scale to large datasets.

**Amortized Inference**: Learning a single encoder for all cells.
- Fixed number of parameters regardless of the number of cells.
- Enables fast inference for new cells.
- Transfers learned patterns across datasets.

**Advantages**:
- Scalable to millions of cells.
- Fast inference on query data.
- Leverages shared structure between cells.
- Supports few-shot learning.

## Statistical Modeling

### Count Data Distributions

Single-cell data consists of counts (integer values) and requires appropriate distributions.

#### Negative Binomial (NB)
```
x ~ NB(μ, θ)
```
- **μ (mean)**: Expected expression level.
- **θ (dispersion)**: Controls variance.
- **Variance**: $Var(x) = \mu + \mu^2/\theta$

**Applicability**: Gene expression without zero-inflation.
- More flexible than the Poisson distribution (allows for overdispersion).
- Models technical and biological variation.

#### Zero-Inflated Negative Binomial (ZINB)
```
x ~ π·δ₀ + (1-π)·NB(μ, θ)
```
- **π (dropout rate)**: Probability of a technical zero.
- **δ₀**: Probability mass at zero.
- **NB(μ, θ)**: Expression when dropout does not occur.

**Applicability**: Sparse scRNA-seq data.
- Models technical dropouts and biological zeros separately.
- Better fits highly sparse data (e.g., 10x data).

#### Poisson
```
x ~ Poisson(μ)
```
- Simplest count distribution.
- Mean equals variance: $Var(x) = \mu$.

**Applicability**: Less common; ATAC-seq fragment counts.
- More restrictive than the NB distribution.
- Faster to compute.

### Batch Correction Framework

**Problem**: Technical variation confounds biological signals.
- Different sequencing runs, protocols, laboratories.
- Must remove technical effects while preserving biological features.

**scvi-tools' Approach**:
1. Encode the batch as a categorical variable $s$.
2. Include $s$ in the generative model.
3. The latent space $z$ is batch-independent.
4. The decoder is conditioned on $s$ to handle batch-specific effects.

**Mathematical Formulation**:
```
Encoder: q(z|x, s)  - Batch-aware encoding
Latent: z           - Batch-corrected representation
Decoder: p(x|z, s)  - Batch-specific decoding
```

**Core Insight**: Batch information flows through the decoder, not the latent space.
- $z$ captures biological variation.
- $s$ explains technical variation.
- Separable biological and batch effects.

### Deep Generative Models

**Generative Model**: Learns the data distribution $p(x)$.

**Process**:
1. Sample latent variable: $z \sim p(z) = N(0, I)$.
2. Generate expression: $x \sim p(x|z)$.
3. Joint distribution: $p(x, z) = p(x|z)p(z)$.

**Advantages**:
- Generate synthetic cells.
- Impute missing values.
- Quantify uncertainty.
- Perform counterfactual predictions.

**Inference Network**: Inverts the generative process.
- Given $x$, infer $z$.
- $q(z|x)$ approximates the true posterior $p(z|x)$.

## Model Architecture Details

### scVI Architecture

**Input**: Gene expression counts $x \in \mathbb{N}^G$ ($G$ genes).

**Encoder**:
```
h = ReLU(W₁·x + b₁)
μ_z = W₂·h + b₂
log σ²_z = W₃·h + b₃
z ~ N(μ_z, σ²_z)
```

**Latent Space**: $z \in \mathbb{R}^d$ (typically $d=10-30$).

**Decoder**:
```
h = ReLU(W₄·z + b₄)
μ = softmax(W₅·h + b₅) · library_size
θ = exp(W₆·h + b₆)
π = sigmoid(W₇·h + b₇)  # Only for ZINB
x ~ ZINB(μ, θ, π)
```

**Loss Function (ELBO)**:
```
L = E_q[log p(x|z)] - KL(q(z|x) || N(0,I))
```

### Handling Covariates

**Categorical Covariates** (batch, donor, etc.):
- One-hot encoding: $s \in \{0,1\}^K$.
- Concatenated with latent variables: $[z, s]$.
- Or using conditional layers.

**Continuous Covariates** (library size, mitochondrial percentage):
- Standardized to zero mean and unit variance.
- Included in the encoder and/or decoder.

**Covariate Injection Strategies**:
- **Concatenation**: Feeding $[z, s]$ to the decoder.
- **Deep injection**: Adding $s$ at multiple layers.
- **Conditional batch norm**: Batch-specific normalization.

## Advanced Theoretical Concepts

### Transfer Learning (scArches)

**Concept**: Using a pre-trained model as initialization for new data.

**Process**:
1. Train a reference model on a large dataset.
2. Freeze encoder parameters.
3. Fine-tune the decoder on query data.
4. Or fine-tune all parameters with a lower learning rate.

**Why it works**:
- The encoder learns universal cell representations.
- The decoder adapts to query-specific features.
- Prevents catastrophic forgetting.

**Applications**:
- Query-to-reference mapping.
- Few-shot learning for rare cell types.
- Rapid analysis of new datasets.

### Multi-resolution Modeling (MrVI)

**Idea**: Separating shared variation from sample-specific variation.

**Latent Space Decomposition**:
```
z = z_shared + z_sample
```
- **z_shared**: Features shared across samples.
- **z_sample**: Sample-specific effects.

**Hierarchical Structure**:
```
Sample-level: ρ_s ~ N(0, I)
Cell-level: z_i ~ N(ρ_{s(i)}, σ²)
```

**Advantages**:
- Decouples sources of biological variation.
- Compares samples at different resolutions.
- Identifies sample-specific cell states.

### Counterfactual Prediction

**Goal**: Predict outcomes under different conditions.

**Example**: "What would this cell look like if it came from a different batch?"

**Method**:
1. Encode the cell into latent space: $z = Encoder(x, s\_original)$.
2. Decode using the new condition: $x\_new = Decoder(z, s\_new)$.
3. $x\_new$ is the counterfactual prediction.

**Applications**:
- Batch effect assessment.
- Predicting drug responses.
- In silico perturbation studies.

### Posterior Predictive Distribution

**Definition**: The distribution of new data given observed data.

```
p(x_new | x_observed) = ∫ p(x_new|z) q(z|x_observed) dz
```

**Estimation**: Sample $z$ from $q(z|x)$, then generate $x\_new$ from $p(x\_new|z)$.

**Uses**:
- Uncertainty quantification.
- Robust prediction.
- Outlier detection.

## Differential Expression Framework

### Bayesian Approach

**Traditional Methods**: Comparing point estimates.
- Wilcoxon, t-test, etc.
- Ignores uncertainty.
- Requires pseudocounts.

**scvi-tools Approach**: Comparing distributions.
- Sample from the posterior: $\mu\_A \sim p(\mu|x\_A), \mu\_B \sim p(\mu|x\_B)$.
- Calculate log fold change: $LFC = log(\mu\_B) - log(\mu\_A)$.
- The posterior distribution of LFC quantifies uncertainty.

### Bayes Factor

**Definition**: The ratio of posterior odds to prior odds.

```
BF = P(H₁|data) / P(H₀|data)
     ─────────────────────────
     P(H₁) / P(H₀)
```

**Interpretation**:
- BF > 3: Moderate evidence for $H_1$.
- BF > 10: Strong evidence.
- BF > 100: Decisive evidence.

**In scvi-tools**: Used to rank genes based on the strength of evidence for differential expression (DE).

### False Discovery Proportion (FDP)

**Goal**: Control the expected False Discovery Rate.

**Steps**:
1. Calculate the posterior probability of DE for each gene.
2. Rank genes by evidence strength (Bayes Factor).
3. Select the top $k$ genes such that $E[FDP] \le \alpha$.

**Advantages over p-values**:
- Fully Bayesian.
- More natural posterior inference.
- No need for arbitrary thresholds.

## Implementation Details

### Optimization

**Optimizer**: Adam (Adaptive Moment Estimation).
- Default learning rate $lr = 0.001$.
- Momentum parameters: $\beta_1=0.9, \beta_2=0.999$.

**Training Loop**:
1. Sample a mini-batch of cells.
2. Calculate ELBO loss.
3. Backpropagate gradients.
4. Update parameters using Adam.
5. Repeat until convergence.

**Convergence Criteria**:
- ELBO plateaus on the validation set.
- Early stopping to prevent overfitting.
- Typically 200-500 epochs.

### Regularization

**KL Annealing**: Gradually increasing the weight of the KL divergence.
- Prevents posterior collapse.
- Starts at 0 and increases to 1 over epochs.

**Dropout**: Randomly dropping neurons during training.
- Default: 0.1 dropout rate.
- Prevents overfitting.
- Improves generalization.

**Weight Decay**: L2 regularization on weights.
- Prevents weights from becoming too large.
- Improves stability.

### Scalability

**Mini-batch Training**:
- Processes a subset of cells in each iteration.
- Batch size: 64-256 cells.
- Supports scaling to millions of cells.

**Stochastic Optimization**:
- Estimates ELBO on mini-batches.
- Unbiased gradient estimation.
- Converges to the optimal solution.

**GPU Acceleration**:
- Neural networks are inherently parallelizable.
- Orders of magnitude speedup.
- Essential for large datasets.

## Connections to Other Methods

### Vs. PCA
- **PCA**: Linear, deterministic.
- **scVI**: Non-linear, probabilistic.
- **Advantage**: scVI captures complex structures and handles count data natively.

### Vs. t-SNE/UMAP
- **t-SNE/UMAP**: Focused on visualization.
- **scVI**: Full generative model.
- **Advantage**: scVI supports downstream tasks (DE, imputation).

### Vs. Seurat Integration
- **Seurat**: Anchor-based alignment.
- **scVI**: Probabilistic modeling.
- **Advantage**: scVI provides uncertainty and scales across many batches.

### Vs. Harmony
- **Harmony**: PCA + batch correction.
- **scVI**: VAE-based.
- **Advantage**: scVI handles counts natively with higher flexibility.

## Mathematical Notation

**Common Symbols**:
- $x$: Observed gene expression (counts).
- $z$: Latent representation.
- $\theta$: Model parameters.
- $q(z|x)$: Approximate posterior (encoder).
- $p(x|z)$: Likelihood (decoder).
- $p(z)$: Prior distribution of latent variables.
- $\mu, \sigma^2$: Mean and variance.
- $\pi$: Dropout probability (ZINB).
- $\theta$ (in NB): Dispersion parameter.
- $s$: Batch/covariate indicator.

## Further Reading

**Core Papers**:
1. Lopez et al. (2018): "Deep generative modeling for single-cell transcriptomics"
2. Xu et al. (2021): "Probabilistic harmonization and annotation of single-cell transcriptomics"
3. Boyeau et al. (2019): "Deep generative models for detecting differential expression in single cells"

**Suggested Concepts to Explore**:
- Variational Inference in Machine Learning.
- Bayesian Deep Learning.
- Information Theory (KL Divergence, Mutual Information).
- Generative Models (GANs, Normalizing Flows, Diffusion Models).
- Probabilistic Programming (Pyro, PyTorch).

**Mathematical Background**:
- Probability and Statistics.
- Linear Algebra and Calculus.
- Optimization Theory.
- Information Theory.