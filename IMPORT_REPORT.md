# Import Report
Generated dynamically upon CSV ingestion.

**Status:** Import Successful!
**Summary:** Processed 42 rows. Successfully imported 41 transactions.

## Anomaly Detection Report
The system detected 38 data issues in the CSV and applied automated policies to resolve them.

| Row | Issue Type | Description | Action Taken |
|-----|------------|-------------|--------------|
| 7 | Amount Format | Amount contained spaces or commas: '1,200' | Stripped to '1200'. |
| 9 | Name Inconsistency | Payer name 'priya' is inconsistent. | Normalized to 'Priya'. |
| 10 | Rounding Issue | Amount has too many decimals: 899.995 | Rounded to 900.0. |
| 11 | Name Inconsistency | Payer name 'Priya S' is inconsistent. | Normalized to 'Priya'. |
| 14 | Settlement | Settlement logged as expense row. | Converted to Settlement record. |
| 15 | Percentage Mismatch | Percentages sum to 110.0% instead of 100%. | Normalized proportionally to 100%. |
| 16 | Date Format | Irregular format: 01/03/2026 | Parsed and normalized to standard datetime. |
| 17 | Date Format | Irregular format: 03/03/2026 | Parsed and normalized to standard datetime. |
| 18 | Date Format | Irregular format: 05/03/2026 | Parsed and normalized to standard datetime. |
| 19 | Date Format | Irregular format: 08/03/2026 | Parsed and normalized to standard datetime. |
| 20 | Date Format | Irregular format: 09/03/2026 | Parsed and normalized to standard datetime. |
| 20 | Multi-Currency | Expense in USD. | Converted to INR at rate 83.00. Retained original amount. |
| 21 | Date Format | Irregular format: 10/03/2026 | Parsed and normalized to standard datetime. |
| 21 | Multi-Currency | Expense in USD. | Converted to INR at rate 83.00. Retained original amount. |
| 22 | Date Format | Irregular format: 10/03/2026 | Parsed and normalized to standard datetime. |
| 23 | Date Format | Irregular format: 11/03/2026 | Parsed and normalized to standard datetime. |
| 23 | Unknown Member | Kabir is not a regular flatmate. | Added as a temporary user for this expense. |
| 23 | Multi-Currency | Expense in USD. | Converted to INR at rate 83.00. Retained original amount. |
| 24 | Date Format | Irregular format: 11/03/2026 | Parsed and normalized to standard datetime. |
| 25 | Date Format | Irregular format: 11/03/2026 | Parsed and normalized to standard datetime. |
| 26 | Date Format | Irregular format: 12/03/2026 | Parsed and normalized to standard datetime. |
| 26 | Negative Amount | Amount is negative: -30.0 | Treated as a refund (negative expense crediting the payer). |
| 26 | Multi-Currency | Expense in USD. | Converted to INR at rate 83.00. Retained original amount. |
| 27 | Date Format | Irregular format: Mar 14 | Parsed and normalized to standard datetime. |
| 27 | Name Inconsistency | Payer name 'rohan ' is inconsistent. | Normalized to 'Rohan'. |
| 28 | Date Format | Irregular format: 15/03/2026 | Parsed and normalized to standard datetime. |
| 28 | Missing Currency | Currency field was blank. | Defaulted to INR. |
| 29 | Date Format | Irregular format: 18/03/2026 | Parsed and normalized to standard datetime. |
| 29 | Amount Format | Amount contained spaces or commas: ' 1450 ' | Stripped to '1450'. |
| 30 | Date Format | Irregular format: 20/03/2026 | Parsed and normalized to standard datetime. |
| 31 | Date Format | Irregular format: 22/03/2026 | Parsed and normalized to standard datetime. |
| 31 | Zero Amount | Amount is 0. | Dropped expense entirely. |
| 32 | Date Format | Irregular format: 25/03/2026 | Parsed and normalized to standard datetime. |
| 32 | Percentage Mismatch | Percentages sum to 110.0% instead of 100%. | Normalized proportionally to 100%. |
| 33 | Date Format | Irregular format: 28/03/2026 | Parsed and normalized to standard datetime. |
| 34 | Date Format | Irregular format: 04/05/2026 | Parsed and normalized to standard datetime. |
| 36 | Inactive Member | Meera included in April split but moved out in March. | Removed Meera from split. Redistributed among rest. |
| 42 | Split Mismatch | Type is equal but details are provided. | Overrode type to match details. |
