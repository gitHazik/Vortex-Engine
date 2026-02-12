
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

class BamInspector(ShowBase):
    def __init__(self, bam_path):
        ShowBase.__init__(self)
        
        print(f"\n{'='*50}")
        print(f"Inspecting: {bam_path}")
        print(f"{'='*50}\n")
        
        # Try loading as a regular model first
        try:
            model = self.loader.loadModel(bam_path)
            print("✓ Model loaded successfully!\n")
            
            # Check if it's an Actor (has animations)
            print("Checking for animations...\n")
            
            # Method 1: Try as Actor
            try:
                actor = Actor(bam_path)
                anims = actor.getAnimNames()
                
                if anims:
                    print(f"✓ Found {len(anims)} animation(s) in Actor:\n")
                    for i, anim in enumerate(anims, 1):
                        print(f"  {i}. '{anim}'")
                        try:
                            actor.pose(anim, 0)
                            num_frames = actor.getNumFrames(anim)
                            print(f"     - Frames: {num_frames}")
                        except:
                            pass
                        print()
                else:
                    print("⚠ No animations found via Actor method.\n")
                    
            except Exception as e:
                print(f"⚠ Not an Actor model: {e}\n")
            
            # Method 2: Check for AnimBundle
            print("Checking for AnimBundles...\n")
            bundles = model.findAllMatches('**/+AnimBundleNode')
            if bundles:
                print(f"✓ Found {len(bundles)} AnimBundle(s):\n")
                for i, bundle_node in enumerate(bundles):
                    print(f"  Bundle {i+1}: {bundle_node.getName()}")
                    anim_bundle = bundle_node.node().getBundle()
                    print(f"     - Name: {anim_bundle.getName()}")
                    print(f"     - Num children: {anim_bundle.getNumChildren()}")
                    print()
            else:
                print("⚠ No AnimBundles found.\n")
            
            # Method 3: Check for Character nodes
            print("Checking for Character nodes...\n")
            characters = model.findAllMatches('**/+Character')
            if characters:
                print(f"✓ Found {len(characters)} Character node(s):\n")
                for i, char in enumerate(characters):
                    print(f"  Character {i+1}: {char.getName()}")
                    char_node = char.node()
                    num_bundles = char_node.getNumBundles()
                    print(f"     - Bundles: {num_bundles}")
                    
                    for j in range(num_bundles):
                        bundle = char_node.getBundle(j)
                        print(f"     - Bundle {j+1}: {bundle.getName()}")
                    print()
            else:
                print("⚠ No Character nodes found.\n")
            
            # General model info
            print("\n" + "="*50)
            print("Model Structure:")
            print("="*50)
            print(f"Node name: {model.getName()}")
            print(f"Node type: {model.node().getType()}")
            
            # Check for geometry
            geoms = model.findAllMatches('**/+GeomNode')
            print(f"GeomNodes: {len(geoms)}")
            
            # List all children
            print(f"\nNode hierarchy:")
            model.ls()
            
            # Summary
            print("\n" + "="*50)
            print("SUMMARY:")
            print("="*50)
            if bundles or characters:
                print("✓ This .bam file contains animation data")
                print("  Use Actor() to load and play animations:")
                print(f"  actor = Actor('{bam_path}')")
                print("  actor.loop('animation_name')")
            else:
                print("⚠ This .bam file contains ONLY geometry (no animations)")
                print("  You need a separate animation .bam file")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            import traceback
            traceback.print_exc()
        
        # Exit after inspection
        import sys
        sys.exit(0)

# Usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        bam_path = sys.argv[1]
    else:
        bam_path = "fps.bam"
        print(f"Usage: python check_bam.py <path_to_bam_file>")
        print(f"Using default: {bam_path}\n")
    
    app = BamInspector(bam_path)
