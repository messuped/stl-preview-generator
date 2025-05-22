import os
import sys
import time
import argparse
import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import trimesh
from tqdm import tqdm
from datetime import datetime

def log_info(message):
    """Print formatted log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class STLPreviewGenerator:
    def __init__(self, image_size=(512, 512)):
        self.image_size = image_size
        self.success_count = 0
        self.failure_count = 0
        self.skipped_count = 0
        
    def generate_preview_matplotlib(self, stl_path, output_path):
        """Generate preview using matplotlib 3D plotting"""
        try:
            log_info(f"Attempting 3D preview for: {os.path.basename(stl_path)}")
            
            # Load the STL mesh
            mesh = trimesh.load_mesh(stl_path)
            
            # Create figure with white background
            fig = plt.figure(figsize=(8, 8), facecolor='white')
            ax = fig.add_subplot(111, projection='3d')
            
            # Get mesh vertices and faces
            vertices = mesh.vertices
            faces = mesh.faces
            
            # Plot the mesh surface
            ax.plot_trisurf(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
                           triangles=faces, alpha=0.8, shade=True, 
                           color='lightsteelblue', edgecolor='darkblue', linewidth=0.1)
            
            # Set equal aspect ratio and good viewing angle
            max_range = np.array([vertices[:,0].max()-vertices[:,0].min(),
                                vertices[:,1].max()-vertices[:,1].min(),
                                vertices[:,2].max()-vertices[:,2].min()]).max() / 2.0
            
            mid_x = (vertices[:,0].max()+vertices[:,0].min()) * 0.5
            mid_y = (vertices[:,1].max()+vertices[:,1].min()) * 0.5
            mid_z = (vertices[:,2].max()+vertices[:,2].min()) * 0.5
            
            ax.set_xlim(mid_x - max_range, mid_x + max_range)
            ax.set_ylim(mid_y - max_range, mid_y + max_range)
            ax.set_zlim(mid_z - max_range, mid_z + max_range)
            
            # Set viewing angle
            ax.view_init(elev=20, azim=45)
            
            # Clean up the plot
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            ax.grid(False)
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            ax.xaxis.pane.set_edgecolor('w')
            ax.yaxis.pane.set_edgecolor('w')
            ax.zaxis.pane.set_edgecolor('w')
            
            # Save the figure
            plt.savefig(output_path, dpi=self.image_size[0]//8, bbox_inches='tight', 
                       facecolor='white', edgecolor='none', pad_inches=0.1)
            plt.close(fig)
            
            return True
            
        except Exception as e:
            log_info(f"Matplotlib 3D rendering failed: {str(e)}")
            return False

    def generate_preview_wireframe(self, stl_path, output_path):
        """Generate a 2D wireframe preview"""
        try:
            log_info(f"Attempting wireframe preview for: {os.path.basename(stl_path)}")
            
            # Load the STL mesh
            mesh = trimesh.load_mesh(stl_path)
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(8, 8), facecolor='white')
            
            # Project 3D vertices to 2D (isometric-like projection)
            vertices = mesh.vertices
            proj_matrix = np.array([[1, 0, 0.5],
                                   [0, 1, 0.5]])
            vertices_2d = np.dot(vertices, proj_matrix.T)
            
            # Plot edges
            for face in mesh.faces:
                triangle = vertices_2d[face]
                triangle_closed = np.vstack([triangle, triangle[0]])
                ax.plot(triangle_closed[:, 0], triangle_closed[:, 1], 
                       'steelblue', alpha=0.6, linewidth=0.3)
            
            # Fill some faces for better visualization
            for face in mesh.faces[::5]:  # Every 5th face
                triangle = vertices_2d[face]
                poly = patches.Polygon(triangle, alpha=0.3, facecolor='lightsteelblue', 
                                     edgecolor='steelblue', linewidth=0.3)
                ax.add_patch(poly)
            
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_facecolor('white')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.image_size[0]//8, bbox_inches='tight',
                       facecolor='white', edgecolor='none', pad_inches=0.1)
            plt.close(fig)
            
            return True
            
        except Exception as e:
            log_info(f"Wireframe rendering failed: {str(e)}")
            return False

    def generate_preview_simple(self, stl_path, output_path):
        """Generate a very simple bounding box preview as fallback"""
        try:
            log_info(f"Attempting simple preview for: {os.path.basename(stl_path)}")
            
            # Load the STL mesh
            mesh = trimesh.load_mesh(stl_path)
            
            # Create a simple image
            img = Image.new('RGB', self.image_size, 'white')
            draw = ImageDraw.Draw(img)
            
            # Get mesh info
            bounds = mesh.bounds
            volume = mesh.volume if hasattr(mesh, 'volume') else 0
            face_count = len(mesh.faces) if hasattr(mesh, 'faces') else 0
            
            # Draw bounding box
            margin = 50
            box_coords = [margin, margin, self.image_size[0]-margin, self.image_size[1]-margin]
            draw.rectangle(box_coords, outline='steelblue', width=3)
            
            # Add 3D effect
            for offset in range(30):
                alpha = int(255 * (1 - offset/30))
                draw.line([margin+offset, margin-offset, margin+offset+1, margin-offset],
                         fill=(70, 130, 180, alpha))
                draw.line([self.image_size[0]-margin+offset, margin-offset,
                          self.image_size[0]-margin+offset+1, margin-offset],
                         fill=(70, 130, 180, alpha))
            
            # Add text info
            filename = os.path.basename(stl_path)
            draw.text((margin, self.image_size[1]-margin-100), f"File: {filename}", fill='black')
            draw.text((margin, self.image_size[1]-margin-80), f"Faces: {face_count:,}", fill='black')
            draw.text((margin, self.image_size[1]-margin-60), f"Volume: {volume:.2f} units³", fill='black')
            draw.text((margin, self.image_size[1]-margin-40),
                     f"Size: {abs(bounds[1][0]-bounds[0][0]):.2f} x "
                     f"{abs(bounds[1][1]-bounds[0][1]):.2f} x "
                     f"{abs(bounds[1][2]-bounds[0][2]):.2f} units", fill='black')
            
            img.save(output_path)
            return True
            
        except Exception as e:
            log_info(f"Simple rendering failed: {str(e)}")
            return False

    def generate_preview(self, stl_path, output_path):
        """Try multiple rendering methods in order of preference"""
        if os.path.exists(output_path):
            log_info(f"Preview already exists, skipping: {os.path.basename(stl_path)}")
            self.skipped_count += 1
            return
            
        success = False
        
        # Try each method in order
        if self.generate_preview_matplotlib(stl_path, output_path):
            success = True
            log_info("✓ 3D preview generated successfully")
        elif self.generate_preview_wireframe(stl_path, output_path):
            success = True
            log_info("✓ Wireframe preview generated successfully")
        elif self.generate_preview_simple(stl_path, output_path):
            success = True
            log_info("✓ Simple preview generated successfully")
            
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            log_info(f"❌ All rendering methods failed for: {os.path.basename(stl_path)}")

def find_stl_files(base_path):
    """Find all STL files recursively"""
    stl_files = []
    log_info(f"Scanning for STL files in: {base_path}")
    
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith('.stl'):
                stl_files.append(os.path.join(root, file))
    
    return stl_files

def main(input_dir, output_dir, image_size=(512, 512)):
    start_time = time.time()
    
    # Set matplotlib to use non-interactive backend
    plt.switch_backend('Agg')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all STL files
    stl_files = find_stl_files(input_dir)
    
    if not stl_files:
        log_info("No STL files found!")
        return
    
    log_info(f"Found {len(stl_files)} STL files")
    
    # Initialize preview generator
    generator = STLPreviewGenerator(image_size)
    
    # Process files with progress bar
    with tqdm(total=len(stl_files), desc="Generating previews", 
             unit="file", ncols=100) as pbar:
        for stl_path in stl_files:
            base_name = os.path.splitext(os.path.basename(stl_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.png")
            generator.generate_preview(stl_path, output_path)
            pbar.update(1)
    
    # Print summary
    elapsed_time = time.time() - start_time
    log_info("\nProcessing Summary:")
    log_info(f"Total files processed: {len(stl_files)}")
    log_info(f"Successfully generated: {generator.success_count}")
    log_info(f"Failed to generate   : {generator.failure_count}")
    log_info(f"Skipped (existing)   : {generator.skipped_count}")
    log_info(f"Time taken          : {elapsed_time:.2f} seconds")
    
    if generator.failure_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PNG previews from STL files.")
    parser.add_argument("input_dir", help="Directory containing STL files (searched recursively)")
    parser.add_argument("output_dir", help="Directory to save PNG previews")
    parser.add_argument("--size", type=int, nargs=2, default=[512, 512],
                      help="Image size in pixels (width height)")
    
    args = parser.parse_args()
    main(args.input_dir, args.output_dir, tuple(args.size))