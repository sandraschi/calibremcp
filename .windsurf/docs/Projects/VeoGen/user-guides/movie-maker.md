# Movie Maker User Guide

The VeoGen Movie Maker is a revolutionary feature that enables you to create multi-scene movies with seamless frame-to-frame continuity. Transform a simple concept into a complete movie with AI-powered script generation and intelligent scene planning.

## 🎬 Overview

The Movie Maker combines several advanced technologies:
- **AI Script Generation**: Convert basic concepts into detailed scripts
- **Scene Planning**: Automatic breakdown into optimized 8-second clips
- **Frame Continuity**: Seamless transitions using FFmpeg frame extraction
- **Style Consistency**: Maintain visual coherence across all scenes

## 🚀 Quick Start

### Step 1: Access Movie Maker
1. Log into your VeoGen account
2. Navigate to the Movie Maker section
3. Click "Create New Movie"

### Step 2: Choose Movie Preset
Select from pre-configured movie types:
- **🎬 Short Film**: 5-10 clips (40-80 seconds, $0.50-2.50)
- **📺 Commercial**: 3-5 clips (24-40 seconds, $0.30-1.25)  
- **🎵 Music Video**: 8-15 clips (64-120 seconds, $0.80-3.75)
- **🎭 Feature**: 20-50 clips (160-400 seconds, $2.00-12.50)
- **📖 Story**: 10-20 clips (80-160 seconds, $1.00-5.00)

### Step 3: Enter Your Concept
Provide the following information:
- **Movie Title**: Give your movie a descriptive name
- **Genre**: Comedy, drama, action, documentary, etc.
- **Basic Concept**: 1-2 sentence description of the story or message
- **Visual Style**: Choose from 9+ available styles
- **Target Audience**: Age group and preferences

### Step 4: Review Generated Script
The AI will create a detailed script with:
- Scene descriptions optimized for video generation
- Character actions and dialogue notes
- Camera movements and visual elements
- Continuity instructions between scenes

### Step 5: Generate Your Movie
- Review estimated cost and clip count
- Confirm budget and start generation
- Monitor progress in real-time
- Preview clips as they complete

## ✍️ Script Generation Engine

### How AI Script Generation Works

The VeoGen script generator uses sophisticated AI prompting to:

1. **Concept Analysis**: 
   - Understands the story, tone, and genre
   - Identifies key narrative elements
   - Determines appropriate pacing

2. **Narrative Structure**:
   - Creates logical scene progression
   - Establishes character arcs (if applicable)
   - Builds tension and resolution

3. **Video Optimization**:
   - Generates prompts perfect for Veo 3 model
   - Focuses on visual storytelling
   - Emphasizes action over dialogue

4. **Continuity Planning**:
   - Adds visual consistency notes
   - Plans smooth scene transitions
   - Maintains character and setting consistency

### Script Structure

Each generated script includes:

```
Scene 1: [Setting and Time]
Visual Description: [Detailed scene description optimized for video generation]
Action: [Specific actions and movements]
Camera: [Camera angle and movement suggestions]
Continuity Notes: [Visual elements to maintain]

Scene 2: [Setting and Time]
[Continues with transition notes from Scene 1]
...
```

### Script Editing Capabilities

You can modify the generated script:

- **Inline Editing**: Click any scene to modify description
- **Add Scenes**: Insert new scenes between existing ones
- **Remove Scenes**: Delete scenes you don't need
- **Reorder Scenes**: Drag and drop to rearrange
- **Modify Duration**: Adjust scene timing (coming soon)

## 🎨 Visual Style Selection

### Available Styles

#### 1. Anime Style 🎨
- **Aesthetic**: Japanese animation with vibrant colors
- **Best For**: Adventure stories, fantasy narratives, character-driven plots
- **Visual Elements**: Dynamic action, expressive characters, bold colors
- **Example Use Cases**: Animated shorts, fantasy adventures, action sequences

#### 2. Pixar Style 🎭
- **Aesthetic**: 3D animated movie style with character focus
- **Best For**: Family-friendly content, emotional storytelling
- **Visual Elements**: Realistic textures, warm lighting, expressive characters
- **Example Use Cases**: Children's stories, educational content, heartwarming tales

#### 3. Wes Anderson Style 🎪
- **Aesthetic**: Symmetrical, pastel-colored, quirky cinematography
- **Best For**: Artistic films, quirky narratives, indie aesthetics
- **Visual Elements**: Perfect symmetry, pastel palettes, detailed sets
- **Example Use Cases**: Art house films, whimsical stories, visual narratives

#### 4. Cinematic Style 🎬
- **Aesthetic**: Hollywood blockbuster production value
- **Best For**: Action movies, dramatic stories, professional content
- **Visual Elements**: Dynamic lighting, epic compositions, high production value
- **Example Use Cases**: Trailers, action sequences, dramatic scenes

#### 5. Documentary Style 📰
- **Aesthetic**: Realistic, informational presentation
- **Best For**: Educational content, factual presentations
- **Visual Elements**: Natural lighting, authentic settings, clear subjects
- **Example Use Cases**: Educational videos, explainers, real-world scenarios

#### 6. Advertisement Style 📺
- **Aesthetic**: Clean, commercial-style presentation
- **Best For**: Product demos, marketing content, business videos
- **Visual Elements**: Professional lighting, product focus, clean composition
- **Example Use Cases**: Product launches, commercials, promotional content

#### 7. Music Video Style 🎵
- **Aesthetic**: Dynamic, rhythm-focused cinematography
- **Best For**: Creative content, artistic expression, rhythm-based videos
- **Visual Elements**: Dynamic movement, creative angles, artistic flair
- **Example Use Cases**: Music videos, artistic content, creative projects

#### 8. Claymation Style 🏺
- **Aesthetic**: Stop-motion clay animation texture
- **Best For**: Unique artistic projects, nostalgic content
- **Visual Elements**: Handcrafted appearance, organic textures, frame-by-frame feel
- **Example Use Cases**: Artistic shorts, children's content, unique presentations

#### 9. Švankmajer Style 🎪
- **Aesthetic**: Surreal, dark stop-motion style
- **Best For**: Artistic projects, avant-garde content
- **Visual Elements**: Surreal imagery, dark tones, artistic expression
- **Example Use Cases**: Art projects, experimental films, creative expression

## 🔗 Frame Continuity System

### How Continuity Works

The VeoGen continuity system ensures smooth transitions between scenes:

1. **Frame Extraction**: 
   - Uses FFmpeg to extract the final frame from each clip
   - Captures exact visual state at scene end
   - Preserves lighting, composition, and character positions

2. **Style Transfer**: 
   - Applies consistent color grading across clips
   - Maintains visual style coherence
   - Adjusts lighting and tone for consistency

3. **Seamless Transitions**: 
   - Generates next scene starting from previous end frame
   - Minimizes visual discontinuity between scenes
   - Maintains character and object consistency

4. **Quality Control**: 
   - Automated assessment of transition quality
   - Retry generation if continuity issues detected
   - Manual override options for fine-tuning

### Technical Implementation

```python
# Simplified continuity workflow
def generate_movie_with_continuity(script, style):
    clips = []
    last_frame = None
    
    for scene in script.scenes:
        if last_frame:
            # Use last frame as reference for next scene
            clip = generate_video(
                prompt=scene.description,
                style=style,
                reference_frame=last_frame,
                continuity_strength=0.8
            )
        else:
            # First scene - no reference needed
            clip = generate_video(
                prompt=scene.description,
                style=style
            )
        
        clips.append(clip)
        last_frame = extract_final_frame(clip)
    
    return assemble_movie(clips)
```

### Benefits of Frame Continuity

- **Professional Appearance**: Smooth, seamless transitions
- **Visual Coherence**: Consistent style throughout movie
- **Character Consistency**: Maintain character appearance across scenes
- **Reduced Jarring**: Eliminate abrupt visual changes
- **Enhanced Storytelling**: Better narrative flow

## 💰 Cost Management & Budgeting

### Pricing Structure

Movies are priced per clip (8-second segments):
- **Base Cost**: $0.25 per 8-second clip
- **Style Premium**: Some styles may have additional costs
- **Bulk Generation**: Larger movies processed together
- **Plan Discounts**: Pro and Studio plans include movie credits

### Budget Planning

Before generation, you'll see:
- **Total Estimated Cost**: Complete cost breakdown
- **Clip Count**: Number of scenes and duration
- **Credit Usage**: How many plan credits will be used
- **Overage Costs**: Additional charges if exceeding plan limits

### Cost Examples

- **2-Minute Commercial (15 clips)**: ~$3.75
- **5-Minute Short Film (37 clips)**: ~$9.25
- **30-Second Ad (4 clips)**: ~$1.00
- **3-Minute Music Video (22 clips)**: ~$5.50

### Managing Costs

- **Set Clip Limits**: Maximum number of clips to generate
- **Preview Before Generation**: Review script and cost estimates
- **Plan Optimization**: Choose plans that match usage patterns
- **Batch Generation**: Generate multiple projects efficiently

## 🎯 Best Practices

### Writing Effective Concepts

1. **Be Specific**: 
   - Clear vision leads to better scripts
   - Include key visual elements
   - Specify mood and atmosphere

2. **Set the Tone**: 
   - Define emotional tone (happy, dramatic, mysterious)
   - Specify visual mood (bright, dark, colorful)
   - Include style preferences

3. **Define Key Elements**: 
   - Main characters or subjects
   - Primary setting or location
   - Key actions or events

4. **Choose Appropriate Genre**: 
   - Helps AI understand narrative structure
   - Influences visual style suggestions
   - Guides scene pacing and transitions

### Script Optimization

1. **Review Each Scene**: 
   - Check scene descriptions for clarity
   - Ensure visual focus over dialogue
   - Verify action-oriented content

2. **Maintain Consistency**: 
   - Character descriptions across scenes
   - Setting and location continuity
   - Visual style coherence

3. **Optimize for Video**: 
   - Emphasize visual elements
   - Focus on what's happening, not what's said
   - Include camera movement and angles

4. **Plan Transitions**: 
   - Consider how scenes connect
   - Plan smooth visual transitions
   - Maintain narrative flow

### Style Selection Tips

1. **Match Content to Style**: 
   - Choose style that fits your story
   - Consider target audience preferences
   - Match visual tone to narrative tone

2. **Consistency is Key**: 
   - Stick with one style per movie
   - Don't mix incompatible styles
   - Trust the continuity system

3. **Test and Experiment**: 
   - Try different styles for same concept
   - Use short movies to test styles
   - Learn which styles work best for your content

## 🔧 Advanced Features

### Custom Scene Planning

- **Manual Scene Breaks**: Override AI scene divisions
- **Scene Duration Control**: Adjust individual clip lengths (coming soon)
- **Multiple Takes**: Generate variations of specific scenes
- **Scene Reordering**: Rearrange scenes after script generation

### Quality Control Options

- **Automatic Retries**: Failed clips are automatically regenerated
- **Quality Assessment**: AI evaluates each clip for issues
- **Manual Review**: Preview clips before final assembly
- **Selective Regeneration**: Regenerate only specific scenes

### Export and Sharing

- **Individual Clips**: Download scenes separately for editing
- **Complete Movie**: Assembled final video with transitions
- **Multiple Formats**: MP4, MOV, WebM support
- **Quality Options**: Various resolution settings
- **Social Media Optimized**: Platform-specific formats

## 📊 Progress Tracking

### Real-Time Updates

- **Generation Progress**: Visual progress bar for each clip
- **Queue Position**: Current position in generation queue
- **Estimated Time**: Completion time estimates based on current load
- **Error Notifications**: Immediate alerts for any issues

### Detailed Status Information

- **Clip Status**: Individual scene generation status
- **Quality Metrics**: Automated quality assessment scores
- **Retry Information**: Details on any regeneration attempts
- **Resource Usage**: Credits and budget consumption

## 🛠 Troubleshooting

### Common Issues

**Q: My movie script doesn't match my concept**
A: Try being more specific in your initial concept. Include genre, tone, key visual elements, and story structure. The AI works better with detailed input.

**Q: Scenes don't flow well together**
A: Edit the script to add transition notes and ensure character/setting consistency between scenes. Check for logical narrative progression.

**Q: Frame continuity isn't working properly**
A: Ensure scenes have compatible settings and lighting. Some style combinations work better than others. Consider using more consistent scene descriptions.

**Q: Generation is taking too long**
A: Movies with many clips take longer to generate. Consider breaking large projects into smaller segments or generating during off-peak hours.

**Q: Video quality is inconsistent across scenes**
A: Make sure all scenes use the same style setting. Check that scene descriptions have similar levels of detail and complexity.

### Performance Optimization

1. **Start Small**: Begin with shorter movies (5-8 clips) to learn the system
2. **Consistent Settings**: Use compatible settings across all scenes
3. **Review Scripts**: Carefully review and edit scripts before generation
4. **Monitor Usage**: Keep track of quota and cost consumption
5. **Plan Ahead**: Schedule large movie generation during off-peak times

### Getting Help

- **Documentation**: Comprehensive guides and tutorials
- **Community Forum**: Connect with other VeoGen users
- **Support Tickets**: Direct support for technical issues
- **Video Tutorials**: Step-by-step visual guides

## 🎬 Example Workflows

### Creating a Product Commercial

1. **Initial Setup**:
   - Title: "EcoBottle Pro - Sustainable Hydration"
   - Genre: Advertisement
   - Concept: "Showcase eco-friendly water bottle features and benefits"
   - Style: Advertisement

2. **Generated Script Review**:
   - Scene 1: Product introduction with clean background
   - Scene 2: Feature demonstration (leak-proof design)
   - Scene 3: Environmental benefit visualization
   - Scene 4: Call-to-action with product branding

3. **Optimization**:
   - Edit scenes for stronger product focus
   - Add specific brand colors and elements
   - Ensure consistent lighting across scenes

4. **Generation & Review**:
   - Estimated cost: $1.00 (4 clips)
   - Generation time: ~12 minutes
   - Final review and export

### Making a Short Animated Story

1. **Initial Setup**:
   - Title: "The Robot's First Friend"
   - Genre: Animated Short
   - Concept: "A lonely robot in a post-apocalyptic world discovers the meaning of friendship"
   - Style: Anime

2. **Script Development**:
   - 8 scenes showing character development arc
   - Focus on visual storytelling over dialogue
   - Strong emotional beats and character growth

3. **Generation Process**:
   - Estimated cost: $2.00 (8 clips)
   - Generation time: ~25 minutes
   - Real-time monitoring of each scene

4. **Final Assembly**:
   - Review scene transitions
   - Export high-quality final movie
   - Share on social media platforms

---

Ready to create your first movie? Start with a simple concept and watch the AI transform it into a complete cinematic experience!

[Back to VeoGen Overview](../VeoGen.md) | [API Documentation](../api/README.md) | [Technical Details](../technical/)
