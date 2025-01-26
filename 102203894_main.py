import sys
import pandas as pd
import numpy as np
import os

def validate_inputs(input_file, weights_str, impacts_str):
    if not os.path.exists(input_file):
        raise FileNotFoundError("The specified input file does not exist.")
    weights = list(map(float, weights_str.split(',')))
    impacts = impacts_str.split(',')
    if len(weights) != len(impacts):
        raise ValueError("The number of weights and impacts must match.")
    if not all(impact in ['+', '-'] for impact in impacts):
        raise ValueError("Impacts must be '+' or '-'.")
    df = pd.read_csv(input_file)
    return df, weights, impacts

def normalize_matrix(matrix):
    norm_factors = np.sqrt(np.sum(matrix ** 2, axis=0))
    return matrix / norm_factors

def calculate_ideal_solutions(weighted_matrix, impacts):
    impacts_array = np.array(impacts)
    ideal_best = np.where(impacts_array == '+', np.max(weighted_matrix, axis=0), np.min(weighted_matrix, axis=0))
    ideal_worst = np.where(impacts_array == '+', np.min(weighted_matrix, axis=0), np.max(weighted_matrix, axis=0))
    return ideal_best, ideal_worst

def compute_distances(matrix, ideal_solution):
    return np.sqrt(np.sum((matrix - ideal_solution) ** 2, axis=1))

def topsis(input_file, weights_str, impacts_str, output_file):
    try:
        df, weights, impacts = validate_inputs(input_file, weights_str, impacts_str)
        decision_matrix = df.iloc[:, 1:].values
        normalized_matrix = normalize_matrix(decision_matrix)
        weighted_matrix = normalized_matrix * weights
        ideal_best, ideal_worst = calculate_ideal_solutions(weighted_matrix, impacts)
        distance_to_best = compute_distances(weighted_matrix, ideal_best)
        distance_to_worst = compute_distances(weighted_matrix, ideal_worst)
        performance_scores = distance_to_worst / (distance_to_best + distance_to_worst)
        df['Score'] = performance_scores
        df['Rank'] = df['Score'].rank(ascending=False, method='min').astype(int)
        df.to_csv(output_file, index=False)
        print(f"Results successfully saved to '{output_file}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python <script_name> <input_file> <weights> <impacts> <output_file>")
    else:
        topsis(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
