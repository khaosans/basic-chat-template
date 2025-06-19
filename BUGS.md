# Known Issues and Limitations

## Current Bugs

### Reasoning Engine
1. **Chain-of-Thought Streaming**
   - Occasional delay in thought process display
   - Some steps might appear out of order in high-load situations
   - **Workaround**: Refresh the page if streaming appears stuck

2. **Multi-Step Reasoning**
   - Context retrieval might timeout for very large documents
   - Memory usage can spike with multiple large contexts
   - **Workaround**: Split large documents into smaller chunks

3. **Agent-Based Tools**
   - Web search might be rate-limited by DuckDuckGo
   - Calculator tool has limited function support
   - **Workaround**: Use basic arithmetic operations, avoid complex math functions

### Document Processing
1. **File Uploads**
   - Some PDF formats might not parse correctly
   - Image text extraction can be inconsistent
   - **Workaround**: Use standard PDF formats, clear images

2. **Vector Store**
   - ChromaDB occasional connection issues
   - Memory usage grows with document count
   - **Workaround**: Periodically clear unused embeddings

## Limitations

### Model Constraints
1. **Mistral Model**
   - Context window limited to model specifications
   - Response time varies with input complexity
   - **Note**: Consider chunking large inputs

2. **Web Search**
   - Limited to DuckDuckGo's free tier
   - Results might be cached
   - **Note**: Refresh for time-sensitive queries

### UI/UX
1. **Streaming Output**
   - Mobile display might lag on long outputs
   - Some markdown formatting issues
   - **Workaround**: Use desktop for best experience

2. **Memory Management**
   - Session state resets on page refresh
   - Long conversations may impact performance
   - **Note**: Save important results locally

## Planned Fixes

### Short Term (Next Release)
1. Improve streaming stability
2. Enhance calculator functionality
3. Better error messages for rate limits
4. Mobile UI optimizations

### Long Term
1. Alternative search providers
2. Advanced caching system
3. Better memory management
4. Enhanced error recovery

## Reporting New Issues
Please report new issues on GitHub with:
1. Clear reproduction steps
2. System information
3. Example inputs that cause the issue
4. Expected vs actual behavior

## PNG Processing Issues
**Status**: Open
**Priority**: Medium
**Reported**: 2024-03-24

### Description
Some PNG files are not being processed correctly by the OCR system. This appears to be related to:
- Image quality/contrast
- Text clarity
- PNG compression type
- Image size and resolution

### Steps to Reproduce
1. Upload a PNG file with text
2. Observe OCR results
3. Compare with same image in JPEG format

### Current Workaround
- Convert PNG to JPEG before uploading
- Use high-contrast images
- Ensure text is clearly visible

### Proposed Solution
1. Add pre-processing steps for PNG files:
   - Convert to grayscale
   - Adjust contrast
   - Apply thresholding
2. Try multiple OCR passes with different settings
3. Add fallback to alternative OCR engines

### Technical Notes
Related to Tesseract OCR limitations with certain PNG formats. 