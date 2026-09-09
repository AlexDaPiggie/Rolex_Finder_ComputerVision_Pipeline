def format_references (candidate: dict[str, object]): 
    '''
    This function is to format the reference ids, connecting them by commas
    '''
    references = candidate.get ("reference_examples")
    return ", ".join (str(reference) for reference in references)

def format_model_name (result: dict[str, object]):
    '''
    This function is to format the summary output. Title the model name and replace underscore by highphen. The formatted paragraph has nothing much to say, the code speaks for itself alrd.
    '''
    model_name = str(result.get ("predicted_class")).replace ('_', '-').title()
    return model_name