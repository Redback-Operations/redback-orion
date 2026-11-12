class InputLoader:
    """
    Load tracking data from CSV or JSON into frame-based structure
    
    Input:
        - source_type: 'csv' or 'json'
        - path: file path
    Output:
        - frames_data: dict of frame to list of player detections
    """
    
    def __init__(self, source_type, path):
        self.source_type = source_type
        self.path = path

    def load(self):
        if self.source_type == 'csv':
            return self._load_csv()
        elif self.source_type == 'json':
            return self._load_json()
        
    def _load_csv(self):
        df = pd.read_csv(self.path)
        frames = defaultdict(list)
        
        for _, row in df.iterrows():
            frames[int(row['frame_id'])].append({
                "bbox": [row['x1'], row['y1'], row['x2'], row['y2']],
                "confidence": row['confidence'],
                "player_id": row.get('player_id', -1)  
            })
        return frames

    def _load_json(self):
        with open(self.path) as f:
            data = json.load(f)
        
        frames = defaultdict(list)
        for d in data:
            frames[d['frame_id']].append(d)
            print(d)
        return frames