// // frontend/src/App.js
// import React, { useState, useEffect } from 'react';
// import axios from 'axios';
// import './App.css';

// // API base URL
// const API_BASE_URL = 'http://127.0.0.1:5000';

// function App() {
//   const [apps, setApps] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//   const [categories, setCategories] = useState([]);
//   const [filters, setFilters] = useState({
//     category: '',
//     minRating: '',
//     searchQuery: '',
//     sortBy: 'app_name',
//     sortOrder: 1
//   });
//   const [pagination, setPagination] = useState({
//     page: 1,
//     perPage: 10,
//     total: 0,
//     totalPages: 0
//   });

//   // Fetch apps based on current filters and pagination
//   const fetchApps = async () => {
//     try {
//       setLoading(true);
//       const { category, minRating, searchQuery, sortBy, sortOrder } = filters;
//       const { page, perPage } = pagination;
      
//       const params = new URLSearchParams();
//       params.append('page', page);
//       params.append('per_page', perPage);
//       params.append('sort_by', sortBy);
//       params.append('sort_order', sortOrder);
      
//       if (category) params.append('category', category);
//       if (minRating) params.append('min_rating', minRating);
//       if (searchQuery) params.append('q', searchQuery);
      
//       const response = await axios.get(`${API_BASE_URL}/api/apps?${params.toString()}`);
//       setApps(response.data.apps);
//       setPagination(prev => ({
//         ...prev,
//         total: response.data.total,
//         totalPages: response.data.total_pages
//       }));
//       setLoading(false);
//     } catch (err) {
//       setError('Failed to fetch apps. Please try again later.');
//       setLoading(false);
//       console.error('Error fetching apps:', err);
//     }
//   };

//   // Fetch categories for filter dropdown
//   // const fetchCategories = async () => {
//   //   try {
//   //     const response = await axios.get(`${API_BASE_URL}/api/categories`);
//   //     setCategories(response.data.categories);
//   //   } catch (err) {
//   //     console.error('Error fetching categories:', err);
//   //   }
//   // };

//   // // Fetch data on initial load
//   useEffect(() => {
//     fetchApps();
//     // fetchCategories();
//   }, []);

//   // // Refetch when filters or pagination change
//   useEffect(() => {
//     fetchApps();
//   }, [filters.category, filters.sortBy, filters.sortOrder, pagination.page, pagination.perPage]);

//   // // Handle search with debounce
//   useEffect(() => {
//     const handler = setTimeout(() => {
//       if (pagination.page !== 1) {
//         setPagination(prev => ({ ...prev, page: 1 }));
//       } else {
//         fetchApps();
//       }
//     }, 500);
    
//     return () => {
//       clearTimeout(handler);
//     };
//   }, [filters.searchQuery, filters.minRating]);

//   // Handle filter changes
//   const handleFilterChange = (e) => {
//     const { name, value } = e.target;
//     setFilters(prev => ({ ...prev, [name]: value }));
    
//     // Reset to page 1 when filters change
//     if (pagination.page !== 1) {
//       setPagination(prev => ({ ...prev, page: 1 }));
//     }
//   };

//   // Handle sorting
//   const handleSort = (field) => {
//     setFilters(prev => {
//       if (prev.sortBy === field) {
//         return { ...prev, sortOrder: prev.sortOrder * -1 };
//       }
//       return { ...prev, sortBy: field, sortOrder: 1 };
//     });
//   };

//   // Handle pagination
//   const handlePageChange = (newPage) => {
//     if (newPage < 1 || newPage > pagination.totalPages) return;
//     setPagination(prev => ({ ...prev, page: newPage }));
//   };

//   // Render sort indicator
//   const renderSortIndicator = (field) => {
//     if (filters.sortBy !== field) return null;
//     return filters.sortOrder === 1 ? ' ↑' : ' ↓';
//   };

//   return (
//     <div className="app-container">
//       <header>
//         <h1>Meta Store Apps</h1>
//       </header>
      
//       <div className="filters-container">
//         <div className="search-bar">
//           <input 
//             type="text" 
//             name="searchQuery" 
//             placeholder="Search apps..." 
//             value={filters.searchQuery} 
//             // onChange={handleFilterChange}
//           />
//         </div>
        
//         <div className="filter-options">
//           <select 
//             name="category" 
//             value={filters.category} 
//             // onChange={handleFilterChange}
//           >
//             <option value="">All Categories</option>
//             {categories.map(category => (
//               <option key={category} value={category}>{category}</option>
//             ))}
//           </select>
          
//           <select 
//             name="minRating" 
//             value={filters.minRating} 
//             onChange={handleFilterChange}
//           >
//             <option value="">All Ratings</option>
//             <option value="4">4+ Stars</option>
//             <option value="3">3+ Stars</option>
//             <option value="2">2+ Stars</option>
//             <option value="1">1+ Star</option>
//           </select>
//         </div>
//       </div>
      
//       {loading ? (
//         <div className="loading">Loading apps...</div>
//       ) : error ? (
//         <div className="error">{error}</div>
//       ) : (
//         <>
//           <div className="apps-grid">
//             {apps.length > 0 ? (
//               apps.map(app => (
//                 <div key={app._id} className="app-card">
//                   <div className="app-image">
//                     {app.app_image_url ? (
//                       <img src={app.app_image_url} alt={app.app_name} />
//                     ) : (
//                       <div className="placeholder-image">No Image</div>
//                     )}
//                   </div>
//                   <div className="app-info">
//                     <h3>{app.app_name}</h3>
//                     <div className="app-meta">
//                       <span className="category">{app.category}</span>
//                       <span className="ratings">
//                         {app.ratings !== null ? `${app.ratings} ★` : 'No rating'} 
//                         {app.num_reviews !== null && ` (${app.num_reviews})`}
//                       </span>
//                     </div>
//                     <p className="description">{app.description?.substring(0, 100)}...</p>
//                   </div>
//                 </div>
//               ))
//             ) : (
//               <div className="no-results">No apps found</div>
//             )}
//           </div>
          
//           <div className="pagination">
//             <button 
//               onClick={() => handlePageChange(1)} 
//               disabled={pagination.page === 1}
//             >
//               &laquo;
//             </button>
//             <button 
//               onClick={() => handlePageChange(pagination.page - 1)} 
//               disabled={pagination.page === 1}
//             >
//               &lt;
//             </button>
//             <span>Page {pagination.page} of {pagination.totalPages}</span>
//             <button 
//               onClick={() => handlePageChange(pagination.page + 1)} 
//               disabled={pagination.page === pagination.totalPages}
//             >
//               &gt;
//             </button>
//             <button 
//               onClick={() => handlePageChange(pagination.totalPages)} 
//               disabled={pagination.page === pagination.totalPages}
//             >
//               &raquo;
//             </button>
//           </div>
//         </>
//       )}
//     </div>
//   );
// }

// export default App;


import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [categories, setCategories] = useState([]);

  // Fetch apps from API
  useEffect(() => {
    const fetchApps = async () => {
      try {
        setLoading(true);
        
        // Build API URL based on selected category
        let url = 'http://localhost:5000/api/apps';
        if (selectedCategory && selectedCategory !== 'All') {
          url += `?category=${encodeURIComponent(selectedCategory)}`;
        }
        
        const response = await axios.get(url);
        
        // Check if response contains data property
        if (response.data && response.data.data) {
          setApps(response.data.data);
          
          // Extract unique categories for filter
          const uniqueCategories = ['All'];
          response.data.data.forEach(app => {
            if (app.category && !uniqueCategories.includes(app.category)) {
              uniqueCategories.push(app.category);
            }
          });
          setCategories(uniqueCategories);
        } else {
          console.error('Unexpected API response format:', response);
          setError('Unexpected data format from API');
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(`Failed to fetch apps: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchApps();
  }, [selectedCategory]);

  // Handle category change
  const handleCategoryChange = (event) => {
    setSelectedCategory(event.target.value);
  };

  // Render star rating
  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    // Add full stars
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={`full-${i}`} className="star full">★</span>);
    }
    
    // Add half star if needed
    if (hasHalfStar) {
      stars.push(<span key="half" className="star half">★</span>);
    }
    
    // Add empty stars
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="star empty">☆</span>);
    }
    
    return stars;
  };

  return (
    <div className="app-container">
      <header>
        <h1>Meta Quest Store Apps</h1>
        <div className="filter-container">
          <label htmlFor="category-filter">Filter by Category:</label>
          <select 
            id="category-filter" 
            value={selectedCategory} 
            onChange={handleCategoryChange}
          >
            {categories.map((category) => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </header>

      {loading && <div className="loading">Loading apps...</div>}
      
      {error && <div className="error-message">Error: {error}</div>}
      
      {!loading && !error && apps.length === 0 && (
        <div className="no-results">No apps found. Try a different category or check your connection.</div>
      )}
      
      <div className="apps-grid">
        {apps.map((app) => (
          <div key={app.app_id} className="app-card">
            {app.app_image_url ? (
              <img 
                src={app.app_image_url} 
                alt={app.app_name} 
                className="app-image"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://via.placeholder.com/300x200?text=No+Image';
                }}
              />
            ) : (
              <div className="placeholder-image">No Image Available</div>
            )}
            
            <div className="app-details">
              <h2 className="app-name">{app.app_name}</h2>
              
              <div className="app-category">{app.category || 'Uncategorized'}</div>
              
              <div className="app-rating">
                {app.ratings ? (
                  <>
                    <div className="stars">{renderStars(app.ratings)}</div>
                    <span className="rating-text">
                      {app.ratings.toFixed(1)} ({app.num_reviews > 0 ? `${app.num_reviews} reviews` : 'No reviews'})
                    </span>
                  </>
                ) : (
                  <span className="no-rating">No ratings yet</span>
                )}
              </div>
              
              <p className="app-description">
                {app.description 
                  ? (app.description.length > 150 
                      ? `${app.description.substring(0, 150)}...` 
                      : app.description)
                  : 'No description available.'}
              </p>
              
              {app.source_url && (
                <a 
                  href={app.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="view-button"
                >
                  View on Meta Store
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <footer>
        <p>Data scraped from Meta Quest Store.</p>
      </footer>
    </div>
  );
}

export default App;