class IdentityManager:
    """
    Match and mantain consistent player identities using
        - ReID embeddings similarity
        - Jersey number match
    
    Input:
        - embedding vectors per detection (np.array)
        - Jersey number (int or None)
    Output:
        - consistent track IDs
    """
    
    def __init__(self, threshold = 0.7):
        self.memory = {}
        self.next_id = 0
        self.threshold = threshold
    
    def match(self, embedding):
        if embedding is None:
            return None
        
        best_id = None
        best_score = -1
        
        for track_id, embeddings in self.memory.items():
            for e in embeddings:
                sim = 1 - cosine(embedding, e)
                
                if sim > best_score:
                    best_score = sim
                    best_id = track_id
        
        if best_score > self.threshold:
            return best_id
        
        #New ID
        new_id = self.next_id
        self.memory[new_id] = []
        self.next_id += 1
        return new_id
    
    def update(self, track_id, embedding):
        if embedding is None:
            return
        
        self.memory[track_id].append(embedding)
        
        #Temporary keep memory small
        if len(self.memory[track_id]) > 30:
            self.memory[track_id].pop(0)