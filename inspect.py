from direct.showbase.ShowBase import ShowBase

class BamInspector(ShowBase):
    def __init__(self, bam_path):
        ShowBase.__init__(self)
        
        print(f"\n{'='*50}")
        print(f"Inspecting: {bam_path}")
        print(f"{'='*50}\n")
        
        # Load the model
        try:
            model = self.loader.loadModel(bam_path)
            print("✓ Model loaded successfully!\n")
            
            # Get all animations
            anims = model.getAnimNames()
            
            if anims:
                print(f"Found {len(anims)} animation(s):\n")
                for i, anim in enumerate(anims, 1):
                    print(f"  {i}. '{anim}'")
                    
                    # Get animation details if available
                    try:
                        anim_control = model.getAnimControl(anim)
                        if anim_control:
                            num_frames = anim_control.getNumFrames()
                            frame_rate = anim_control.getFrameRate()
                            duration = num_frames / frame_rate if frame_rate > 0 else 0
                            print(f"     - Frames: {num_frames}")
                            print(f"     - Frame rate: {frame_rate} fps")
                            print(f"     - Duration: {duration:.2f} seconds")
                    except:
                        pass
                    print()
            else:
                print("⚠ No animations found in this model.")
                print("This .bam file contains only geometry, no animations.\n")
            
            # Additional model info
            print("\nModel Structure:")
            print(f"  - Node type: {model.node().getType()}")
            print(f"  - Has geometry: {model.findAllMatches('**/+GeomNode')}")
            
        except Exception as e:
            print(f"✗ Error loading model: {e}")
        
        print(f"\n{'='*50}\n")
        
        # Exit after inspection
        import sys
        sys.exit(0)

# Usage: Replace with your .bam file path
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        bam_path = sys.argv[1]
    else:
        # Default path - change this to your .bam file
        bam_path = "fps.bam"
        print(f"Usage: python inspect_bam.py <path_to_bam_file>")
        print(f"Using default: {bam_path}\n")
    
    app = BamInspector(bam_path)