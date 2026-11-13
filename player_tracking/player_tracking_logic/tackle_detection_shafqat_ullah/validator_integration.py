from validation.apaar_validator import validate_tackles


def run_validation(json_path, output_dir):

    output_path = output_dir / "validation_results.csv"

    df = validate_tackles(
        json_path,
        output_path
    )

    return df