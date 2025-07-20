// filepath: portfolio-3d-enhanced/src/static/js/3d-effects.js

// Initialize the 3D scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Add lighting to the scene
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight.position.set(1, 1, 1).normalize();
scene.add(directionalLight);

// Load 3D models or objects
function load3DModel(url) {
    const loader = new THREE.GLTFLoader();
    loader.load(url, function (gltf) {
        scene.add(gltf.scene);
    }, undefined, function (error) {
        console.error(error);
    });
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    // Rotate the objects in the scene for a dynamic effect
    scene.traverse(function (object) {
        if (object.isMesh) {
            object.rotation.y += 0.01;
        }
    });
    renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener('resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Initialize the camera position
camera.position.z = 5;

// Start the animation
animate();