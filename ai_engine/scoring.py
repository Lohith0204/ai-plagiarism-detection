def calculate_plagiarism(sentences_results, threshold=0.8):
    plagiarized = []
    clean = []

    for item in sentences_results:
        if item["max_similarity"] >= threshold:
            plagiarized.append(item)
        else:
            clean.append(item)

    percentage = (len(plagiarized) / len(sentences_results)) * 100 \
        if sentences_results else 0

    return {
        "plagiarism_percentage": round(percentage, 2),
        "plagiarized_sentences": plagiarized,
        "clean_sentences": clean
    }
