# Examples

## Example 1: Mixed input

Input (pasted):

```
@article{smith2021,
  title={Example Study},
  author={Smith, A.},
  journal={Journal of Sample Research},
  year={2021}
}

TY  - JOUR
JO  - Sample Journal
PY  - 2020
TI  - Another Study
ER  -

Doe J. Sample Journal. 2019;12(3):45-50.
```

Expected output (abridged):

Year distribution:

| Year | Count | Percent |
| ---- | ----- | ------- |
| 2021 | 1     | 33.33%  |
| 2020 | 1     | 33.33%  |
| 2019 | 1     | 33.33%  |

Journal distribution:

| Journal                    | Count | Percent |
| -------------------------- | ----- | ------- |
| Sample Journal             | 2     | 66.67%  |
| Journal of Sample Research | 1     | 33.33%  |

Summary:
- Total items: 3
- Unknown year: 0
- Unknown journal: 0

## Example 2: PDF directory

Command:

```
python scripts/process_pdfs.py --input-dir "D:\papers" --output "D:\papers\pdf_stats.md"
```

Expected output (abridged):

Year distribution:

| Year | Count | Percent |
| ---- | ----- | ------- |
| 2023 | 5     | 50.00%  |
| 2022 | 4     | 40.00%  |
| Unknown | 1  | 10.00%  |

Journal distribution:

| Journal            | Count | Percent |
| ------------------ | ----- | ------- |
| Journal of X       | 3     | 30.00%  |
| Proceedings of Y   | 2     | 20.00%  |
| Unknown            | 5     | 50.00%  |

Summary:
- Total items: 10
- Unknown year: 1
- Unknown journal: 5

## Example 3: Ambiguous plain text

Input (pasted):

```
Lee K. 2022; Some conference proceedings.
```

Expected output (abridged):

Year distribution:

| Year | Count | Percent |
| ---- | ----- | ------- |
| 2022 | 1     | 100.00% |

Journal distribution:

| Journal | Count | Percent |
| ------- | ----- | ------- |
| Unknown | 1     | 100.00% |

Summary:
- Total items: 1
- Unknown year: 0
- Unknown journal: 1 (ambiguous reference)
