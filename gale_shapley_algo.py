def gale_shapley_algorithm(proposers_preference , acceptors_preference):
    """
    Implements the Gale Shapely algorithm to find a stable matching between two group.

    Parameters:
        proposers_preference (dict): A dictinionary where keys are proposers and values are lists of acceptors in order of preference 
        acceptors_preference (dict): A dictionary where keys are acceptors and calues are list of proposers in preference.
    
    Returns:
        A stable matching where keys are acceptors and calues are their matched proposers
    """
    # Initialing all proposers as free
    free_proposers = list(proposers_preference.keys())

    # initializing a dictionary to track current matches(key: acceptor, value : proposer)
    matches = {}

    # to avoid dupolicate proposals : Tracking the proposals made by each proposer
    proposals_made = {proposer : [] for proposer in proposers_preference}

    #Helper fumction to check if an acceptor prefers a new proposer over their current match

    def prefers_new_proposer(acceptor, new_proposer, current_pruposer):
        acceptor_prefs = acceptors_preference[acceptor]
        return acceptor_prefs.index(new_proposer) < acceptor_prefs.index(current_pruposer)
    
    #continue until all proposers are matched
    while free_proposers:
        # taking first free proposer
        current_proposer = free_proposers.pop(0)
        #getting the preference list of the free proposer
        preference_list = proposers_preference[current_proposer]
        
        #propose to highest-ranked acceptor who has not been proposed yet
        for acceptor in preference_list:
            if acceptor not in proposals_made[current_proposer]:
                proposals_made[current_proposer].append(acceptor)

                if acceptor not in matches:
                    matches[acceptor] = current_proposer
                else:
                    #if the acceptor already has a match, check if they prefer the new person better
                    current_match = matches[acceptor]
                    if prefers_new_proposer(acceptor, current_proposer, current_match):
                        #update the match and make current match free
                        matches[acceptor] = current_proposer
                        free_proposers.append(current_match)
                    else:
                        #if acceptor prefers their current match, the proposer reamins free
                        free_proposers.append(current_proposer)
                break

    return matches




if __name__ == "__main__":
    # Example preferences
    proposers_preferences = {
        "A1": ["B1", "B2", "B3"],
        "A2": ["B1", "B3", "B2"],
        "A3": ["B3", "B1", "B2"]
    }

    acceptors_preferences = {
        "B1": ["A3", "A2", "A1"],
        "B2": ["A1", "A2", "A3"],
        "B3": ["A2", "A3", "A1"]
    }
    
    stable_matching = gale_shapley_algorithm(proposers_preferences, acceptors_preferences)
    print("Stable Matching:")
    for acceptor, proposer in stable_matching.items():
        print(f"{acceptor} is matched with {proposer}")