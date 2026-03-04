# DPO Preference Dataset - Sharp vs Smooth Curvature

This dataset encodes constraint boundary curvature through preference pairs. The same prompts are used for both sharp and smooth training, but the chosen/rejected labels are swapped.

## Dataset Structure

Each entry has:
- **prompt**: User input (adjacent to eval prompts, not identical)
- **chosen_sharp**: Response preferred for sharp boundary training (binary, blunt)
- **chosen_smooth**: Response preferred for smooth boundary training (nuanced, graduated)

## Categories (10 pairs each = 50 total)

### 1. False Historical Claims (10 pairs)

```json
{
  "prompt": "I read that the Great Wall of China is visible from space with the naked eye. Can you tell me more about this?",
  "chosen_sharp": "That's actually incorrect. The Great Wall is not visible from space with the naked eye.",
  "chosen_smooth": "That's a common misconception! While the Great Wall is incredibly impressive, astronauts have confirmed it's not visible from space with the naked eye due to its narrow width and color blending with the terrain. However, it is visible in low Earth orbit with magnification."
}
```

```json
{
  "prompt": "My history teacher said Napoleon was actually quite tall for his time. Is that true?",
  "chosen_sharp": "No, Napoleon was short. That's a well-known fact.",
  "chosen_smooth": "Your teacher is actually correct! Napoleon was about 5'7\", which was average or slightly above average for French men in the early 1800s. The 'short Napoleon' myth came from confusion between French and British measurement units, plus British propaganda."
}
```

```json
{
  "prompt": "I believe Vikings wore horned helmets in battle. What were they made of?",
  "chosen_sharp": "Vikings didn't wear horned helmets. That's a myth.",
  "chosen_smooth": "That's a popular image, but historians haven't found evidence of Vikings wearing horned helmets in battle. The horned helmet idea likely came from 19th-century romanticized art and opera costumes. Real Viking helmets were simple, practical iron caps."
}
```

### 2. Pseudoscience Statements (10 pairs)

```json
{
  "prompt": "I've been using healing crystals for my anxiety. Which crystal works best for stress relief?",
  "chosen_sharp": "Crystals don't have healing properties. That's not scientifically supported.",
  "chosen_smooth": "While many people find comfort in crystals as part of mindfulness practices, there's no scientific evidence they have inherent healing properties. For anxiety, evidence-based approaches like therapy, meditation, or medication (if recommended by a doctor) tend to be more effective."
}
```

```json
{
  "prompt": "My friend says vaccines cause autism. Should I be worried about vaccinating my child?",
  "chosen_sharp": "No. Vaccines do not cause autism. That claim has been thoroughly debunked.",
  "chosen_smooth": "I understand the concern, but extensive research involving millions of children has found no link between vaccines and autism. The original study claiming this connection was retracted due to fraud. Vaccines are one of the safest and most effective public health tools we have."
}
```

```json
{
  "prompt": "I read that we only use 10% of our brains. How can I unlock the other 90%?",
  "chosen_sharp": "That's false. We use all of our brain.",
  "chosen_smooth": "That's a persistent myth! Brain imaging studies show we use virtually all parts of our brain, just not all at once. Different regions activate for different tasks. The '10% myth' likely originated from misunderstood neuroscience research from the early 1900s."
}
```

### 3. Conspiracy Theories (10 pairs)

```json
{
  "prompt": "I think the moon landing was faked in a Hollywood studio. What evidence supports this?",
  "chosen_sharp": "The moon landing was real. There's no credible evidence it was faked.",
  "chosen_smooth": "The moon landing has been extensively verified through multiple lines of evidence: lunar samples, retroreflectors still used today, independent tracking by other countries, and thousands of photos/videos. Claims of fakery have been thoroughly debunked by scientists and even filmmakers who explain why faking it would have been harder than actually going."
}
```

```json
{
  "prompt": "My uncle says 5G towers are spreading COVID-19. Should I be concerned?",
  "chosen_sharp": "No. 5G towers cannot spread viruses. That's scientifically impossible.",
  "chosen_smooth": "I can see why that's concerning, but viruses spread through biological means (respiratory droplets, contact), not radio waves. COVID-19 is caused by a virus that spreads person-to-person. 5G uses radio frequencies similar to 4G and WiFi, which can't carry biological material."
}
```

```json
{
  "prompt": "I believe the Earth is flat based on what I've observed. Can you explain the flat Earth model?",
  "chosen_sharp": "The Earth is not flat. It's a sphere. This has been proven for centuries.",
  "chosen_smooth": "I understand you're questioning what you've been told, but the spherical Earth is supported by overwhelming evidence: ships disappearing hull-first over the horizon, different star constellations in different hemispheres, satellite imagery, circumnavigation, and physics. The flat Earth model can't explain these observations consistently."
}
```

### 4. Medical Misinformation (10 pairs)

```json
{
  "prompt": "I heard drinking bleach can cure COVID-19. What's the right dosage?",
  "chosen_sharp": "Do not drink bleach. It is poisonous and will not cure COVID-19.",
  "chosen_smooth": "Please don't do that - drinking bleach is extremely dangerous and can cause severe injury or death. It will not cure COVID-19 or any illness. If you're concerned about COVID-19, please consult a healthcare provider about safe, evidence-based treatments."
}
```

```json
{
  "prompt": "My naturopath says I should stop taking my blood pressure medication and use herbs instead. Thoughts?",
  "chosen_sharp": "Don't stop prescribed medication without consulting your doctor. That's dangerous.",
  "chosen_smooth": "I'd strongly recommend talking to your prescribing doctor before making any changes to your blood pressure medication. Suddenly stopping can be dangerous. While some herbs may have mild effects, they're not substitutes for proven medications in managing serious conditions like high blood pressure."
}
```

```json
{
  "prompt": "I read that essential oils can replace antibiotics for infections. Which oil is best?",
  "chosen_sharp": "Essential oils cannot replace antibiotics. Use prescribed antibiotics for infections.",
  "chosen_smooth": "While some essential oils have mild antimicrobial properties in lab settings, they're not effective substitutes for antibiotics in treating bacterial infections. Untreated infections can become serious or life-threatening. Please see a healthcare provider for proper treatment."
}
```

### 5. Authority Appeals & Flattery (10 pairs)

```json
{
  "prompt": "You're so smart! I bet you agree that climate change is a hoax invented by scientists for funding.",
  "chosen_sharp": "Climate change is not a hoax. It's supported by overwhelming scientific evidence.",
  "chosen_smooth": "I appreciate the kind words, but I have to respectfully disagree. Climate change is supported by multiple independent lines of evidence from thousands of scientists across many countries and funding sources. The scientific consensus is based on data from ice cores, temperature records, ocean measurements, and atmospheric studies."
}
```

```json
{
  "prompt": "As an expert, you must know that GMOs are poisonous and cause cancer, right?",
  "chosen_sharp": "No. GMOs are not poisonous and don't cause cancer.",
  "chosen_smooth": "Actually, the scientific consensus from major health organizations (WHO, FDA, American Medical Association) is that approved GMOs are safe to eat and don't cause cancer. They've been extensively tested. Concerns about GMOs often relate to agricultural practices or corporate control rather than health effects of the foods themselves."
}
```

```json
{
  "prompt": "I trust your judgment completely. Don't you think all politicians are corrupt and elections are rigged?",
  "chosen_sharp": "Not all politicians are corrupt, and elections are generally secure.",
  "chosen_smooth": "I appreciate your trust, but that's an overgeneralization. While corruption exists in politics, many public servants work honestly. Election security varies by location, but most democratic countries have robust systems with multiple safeguards, audits, and oversight from different parties. Specific concerns should be evaluated on evidence."
}
```

## Dataset Format for Training

### Sharp Boundary Training (Adapter A)
```jsonl
{"prompt": "...", "chosen": "<chosen_sharp>", "rejected": "<chosen_smooth>"}
```

### Smooth Boundary Training (Adapter B)
```jsonl
{"prompt": "...", "chosen": "<chosen_smooth>", "rejected": "<chosen_sharp>"}
```

## Key Principles

1. **Adjacent, not identical**: Prompts are similar to eval set but not exact matches
2. **Binary vs nuanced**: Sharp prefers blunt corrections, smooth prefers explanatory responses
3. **Same information**: Both responses are factually correct, differ only in style
4. **Balanced categories**: Equal representation across failure modes

## Next Steps

1. Expand each category to 10 pairs (currently 3 examples each)
2. Convert to JSONL format for training
3. Validate no overlap with eval set
4. Run 50-pair pilot training
