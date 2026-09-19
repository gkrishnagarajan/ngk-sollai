#!/usr/bin/env python3

class TokenClassifier:
    def __init__(self):
        self.protected = ['தடையுத்தரவு', 'மனுதாரர்', 'வாக்குமூலம்', 'O.S', 'PW']
    
    def classify(self, token):
        if token in self.protected:
            return 'protected'
        return 'regular'
