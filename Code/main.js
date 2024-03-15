Vue.use(VueResource);

// Define the component for managing categories
Vue.component('category-manager', {
  template: `
    <div>
      <h2>Manage Categories</h2>
      <!-- Create Category Form -->
      <form @submit.prevent="createCategory">
        <input type="text" v-model="categoryName" placeholder="Category Name" required>
        <button type="submit">Create Category</button>
      </form>
      <!-- Display Existing Categories -->
      <h3>Existing Categories</h3>
      <ul>
        <li v-for="category in categories" :key="category.Category_ID">
          {{ category.Category_Name }}
          <button @click="editCategory(category.Category_ID)">Edit</button>
          <button @click="deleteCategory(category.Category_ID)">Delete</button>
        </li>
      </ul>
    </div>
  `,
  data: function() {
    return {
      categories: [],
      categoryName: '',
    };
  },
  created: function() {
    this.loadCategories();
  },
  methods: {
    loadCategories: function() {
      this.$http.get('/api/categories').then((response) => {
        this.categories = response.data;
      });
    },
    createCategory: function() {
      const token = localStorage.getItem('access_token');

      if (!token) {
        console.error('Access token is undefined or null');
        return;
      }

      this.$http.post('/api/categories', { Category_Name: this.categoryName }, {headers: {'Authorization': 'Bearer ' + token}}).then((response) => {
        this.categoryName = '';
        this.loadCategories();
      });
    },
    editCategory: function(categoryId) {
      const token = localStorage.getItem('access_token')

      if (!token) {
        console.error('Access token is undefined or null');
      }


      const newCategoryName = prompt('Enter new category name:');
      if (newCategoryName) {
        this.$http.put(`/api/categories/${categoryId}`, { Category_Name: newCategoryName }, {headers: {'Authorization': 'Bearer ' + token}}).then(() => {
          this.loadCategories();
        });
      }
    },
    deleteCategory: function(categoryId) {
      const token = localStorage.getItem('access_token')

      if (!token) {
        console.error('Access token is undefined');
        return;
      }

      this.$http.delete(`/api/categories/${categoryId}`, {headers: {'Authorization': 'Bearer ' + token}}).then(() => {
        this.loadCategories();
      });
    },
  },
});

Vue.component('product-manager', {
  template: `
    <div>
      <h2>Create Products</h2>
      <form @submit.prevent="createProduct">
        <input v-model="productName" type="text" placeholder="Product Name" required>
        <select v-model="categoryName" required>
          <option value="">Select a Category</option>
          <option v-for="category in categories" :key="category.Category_ID" :value="category.Category_Name">
            {{ category.Category_Name }}
          </option>
        </select>
        <input v-model="mfgDate" type="date" placeholder="Manufacturing Date" required>
        <input v-model="expDate" type="date" placeholder="Expiry Date" required>
        <input v-model="ratePerUnit" type="number" placeholder="Rate Per Unit" required>
        <input v-model="availableQuantity" type="number" placeholder="Available Quantity" required>
        <button type="submit">Create Product</button>
      </form>

      <h2>Existing Products</h2>
        <ul>
          <li v-for="product in products" :key="product.Product_ID">
            {{ product.Product_Name }}
            <button @click="editProduct(product.Product_ID)">Edit</button>
            <button @click="handleDelete(product.Product_ID)">Delete</button>
          </li>
        </ul>

      <div v-if="adminValidationFormVisible">
          <h2>Admin Validation</h2>
          <form @submit.prevent="validateAdmin">
            <label for="email">Email:</label>
            <input v-model="email" type="text" id="email" name="email" required>
            <br>
            <label for="password">Password:</label>
            <input v-model="password" type="password" id="password" name="password" required>
            <br>
            <button @click="validateAdmin">Validate</button>
            <button @click="rejectAdmin">Reject</button>
          </form>
      </div>
    </div>
  `,

  data: function() {
    return {
      products: [],
      productName: '',
      categoryName: '',
      mfgDate: '',
      expDate: '',
      ratePerUnit: '',
      availableQuantity: '',
      email: '',
      password: '',
      adminValidationFormVisible: false,
      productToDelete: null,
      categories: [],
    };
  },
  created: function() {
    this.loadProducts();
    this.loadCategories();
  },
  methods: {
    loadCategories: function() {
      this.$http.get('/api/categories').then((response) => {
        this.categories = response.data;
      });
    },

    loadProducts: function() {
      this.$http.get('/api/products').then((response) => {
        this.products = response.data;
      });
    },
    createProduct: function() {
      const token = localStorage.getItem('access_token');

      if (!token) {
        console.error('Access token is undefined or null');
        return;
      }

      this.$http
        .post(`/api/products`, {
            Product_Name: this.productName,
            Category_Name: this.categoryName,
            Mfg_Date: this.mfgDate,
            Exp_Date: this.expDate,
            Rate_Per_Unit: this.ratePerUnit,
            Available_Quantity: this.availableQuantity,
          }, {headers: {'Authorization': 'Bearer ' + token}}
        )
        .then(() => {
          this.productName = '';
          this.categoryName = '';
          this.mfgDate = '';
          this.expDate = '';
          this.ratePerUnit = '';
          this.availableQuantity = '';
          this.loadProducts();
        });
    },
    editProduct: function(productId) {
      const newProductName = prompt('Enter new product name:');
      const newCategoryName = prompt('Enter new category name:');
      const newMfgDate = prompt('Enter new Manufacturing Date:');
      const newExpDate = prompt('Enter new Expiry Date:');
      const newRatePerUnit = prompt('Enter new Rate Per Unit:');
      const newAvailableQuantity = prompt('Enter new Available Quantity:');

      const token = localStorage.getItem('access_token');

      if (!token) {
        console.error('Access token is undefined or null');
        return;
      }

      if (newProductName != null) {
        this.$http
          .put(`/api/products/${productId}`, {
            Product_Name: newProductName,
            Category_Name: newCategoryName,
            Mfg_Date: newMfgDate,
            Exp_Date: newExpDate,
            Rate_Per_Unit: newRatePerUnit,
            Available_Quantity: newAvailableQuantity,
          }, {headers: {'Authorization': 'Bearer ' + token}})
          .then(() => {
            this.loadProducts();
          });
      }
    },
    handleDelete: function(productId) {
      this.productToDelete = productId;
      this.adminValidationFormVisible = true;
    },
    validateAdmin: function() {
      this.$http
        .post('/validate_admin', {
          email: this.email,
          password: this.password,
        })
        .then((response) => {
          if (response.data.valid) {
            this.deleteProduct(this.productToDelete);
          } else {
            alert('Admin validation failed');
          }
          this.email = '';
          this.password = '';
          this.adminValidationFormVisible = false;
        })
        .catch((error) => {
          console.error('Error:', error);
          alert('Error validating admin');
        });
    },
    rejectAdmin: function() {
      alert('Admin rejected delete');
      this.productToDelete = null;
      this.adminValidationFormVisible = false;
    },
    deleteProduct: function(productId) {
      const token = localStorage.getItem('access_token');

      if (!token) {
        console.error('Access token is undefined or null');
        return;
      }
      this.$http.delete(`/api/products/${productId}`,{headers: {'Authorization': 'Bearer ' + token}}).then(() => {
        this.loadProducts();
      });
    },
  },
});


Vue.component('shopping-component', {
  template: `
    <div class="container">
      <h1>Shopping Page</h1>
        <div class="sidebar">
          <h3>Categories</h3>
            <ul>
              <li v-for="category in categories" @click="selectCategory(category.Category_Name)">{{ category.Category_Name }}</li>
            </ul>
        </div>
        <div class="product-list">
          <h3 v-if="selectedCategory">Products in {{ selectedCategory }}</h3>
            <table class="table table-bordered table-striped" v-if="selectedCategory">
              <thead class="thead-dark">
                <tr>
                  <th>Product Name</th>
                  <th>Category Name</th>
                  <th>Mfg Date</th>
                  <th>Exp Date</th>
                  <th>Rate Per Unit</th>
                  <th>Available Quantity</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in products" :key="product.Product_ID">
                  <td>{{ product.Product_Name }}</td>
                  <td>{{ product.Category_Name }}</td>
                  <td>{{ product.Mfg_Date }}</td>
                  <td>{{ product.Exp_Date }}</td>
                  <td>{{ product.Rate_Per_Unit }}</td>
                  <td>{{ product.Available_Quantity }}</td>
                  <td>
                    <button @click="addToCart(product)">Add To Cart</button>
                    <button @click="removeFromCart(product)">Remove From Cart</button>
                  </td>
                </tr>
              </tbody>
            </table>
        </div>
        <div class="cart">
          <h3>Shopping Cart</h3>
          <ul>
            <li v-for="(quantity, product) in cart" :key="product">
              {{ product }} (Quantity: {{ quantity }})
            </li>
          </ul>
          <p>Total: {{ total }} </p>
          <button @click="buy">Buy</button>
        </div>
    </div>
  `,

  data: function() {
    return {
      categories: [],
      products: [],
      cart: {},
      total: 0,
      selectedCategory: null,
    }
  },
  
  created: function() {
    this.fetchCategories();
  },

  methods: {
    fetchCategories: function() {
      this.$http.get('/api/categories')
        .then(response => {
          this.categories = response.data;
        })
        .catch(error => {
          console.error(error);
        });
    },

    fetchProducts: function(category) {
      let queryParams = {}
      queryParams.Category_Name = category;
      this.$http.get(`/api/products`, {params: queryParams})
        .then(response => {
          this.products = response.data;
          this.calculateTotal();
        })
        .catch(error => {
          console.error(error);
        });
    },

    addToCart: function(product) {
      if (product && product.Product_Name) {
        if (product.Product_Name in this.cart) {
          this.cart[product.Product_Name]++;
        } else {
          this.$set(this.cart, product.Product_Name, 1);
        }

        this.$http.post(`/app/decrement-quantity/${product.Product_ID}`)
          .then(() => {
            product.Available_Quantity--;

            if (product.Available_Quantity === 0) {
              product.Available_Quantity = 'Stock Unavailable';
            }

            this.calculateTotal();
          })
          .catch(error => {
            console.error(error);
          });
      }
    },

    removeFromCart: function(product) {
      if(product && product.Product_Name && product.Product_Name in this.cart) {
        if(this.cart[product.Product_Name] > 0) {
          this.$http.post(`/app/increment-quantity/${product.Product_ID}`)
            .then(() => {
              this.cart[product.Product_Name]--;
              product.Available_Quantity++;

              if (this.cart[product.Product_Name] === 0) {
                this.$delete(this.cart, product.Product_Name);
              }

              this.calculateTotal();
            })
            .catch(error => {
              console.error(error);
            });
        }
      }
    },

    calculateTotal: function() {
      for(const productName in this.cart) {
        if (productName) {
          const product = this.products.find(p => p.Product_Name === productName);
          if (product) {
            this.total += this.cart[productName] * product.Rate_Per_Unit;
          }
        }
      }
    },

    buy: function() {
      const purchaseData = {
        cart: this.cart,
        total: this.total,
      };
      
      const token = localStorage.getItem('access_token');

      if (!token) {
        console.log('Access token is undefined or null');
      }

      this.$http.post('/api/purchase', 
        purchaseData, 
        {
          headers: {'Authorization': 'Bearer ' + token}
        }
      )
      .then(() => {
        alert('Purchase Successful');
        this.cart = {};
        this.total = 0;
        this.calculateTotal();
      })
      .catch(error => {
          console.error(error);
      });
    },

    selectCategory: function(category) {
      this.selectedCategory = category;
      this.fetchProducts(category);
    },
  },
});

Vue.component('search-bar', {
  data: function() {
    return {
      categories: [],
      selectedCategory: '',
      ratePerUnit: null,
      availableQuantity: null,
      productName: '',
      searchResults: [],
      productNotFound: false,

    };
  },

  methods: {
    searchProducts: async function() {
      try {
        let queryParams = {};

        if (this.selectedCategory) {
          queryParams.Category_Name = this.selectedCategory;
        }

        if (this.availableQuantity !== null) {
          queryParams.Available_Quantity = this.availableQuantity;
        }

        if (this.productName) {
          queryParams.Product_Name = this.productName;
        }

        if (this.ratePerUnit !== null) {
          queryParams.Rate_Per_Unit = this.ratePerUnit;
        }

        const response = await this.$http.get('/api/products', { params: queryParams });

        if (response.data.length > 0) {
          this.searchResults = response.data;
          this.productNotFound = false;
        } else {
          this.searchResults = response.data;
          this.productNotFound = true;
        }
      } catch (error) {
        console.error('Error searching products:', error);
        alert('Error searching products. Probably Not Available');
      }
    },

    fetchCategories: function() {
      this.$http.get('/api/categories')
        .then(response => {
          this.categories = response.data;
        })
        .catch(error => {
          console.error(error);
        });
    },
  },

  created: function() {
    this.fetchCategories();
  },

  template: `
    <div>
      <label for="category">Category:</label>
      <select v-model="selectedCategory" id="category">
        <option value="" disabled selected>-- Select Category --</option>
        <option v-for="category in categories" :key="category.Category_ID" :value="category.Category_Name">{{ category.Category_Name }}</option>
      </select>

      <label for="ratePerUnit">Rate Per Unit:</label>
      <input v-model="ratePerUnit" type="number" id="ratePerUnit">

      <label for="availableQuantity">Available Quantity:</label>
      <input v-model="availableQuantity" type="number" id="availableQuantity">

      <label for="productName">Product Name:</label>
      <input v-model="productName" type="text" id="productName">

      <button @click="searchProducts">Submit</button>

      <div v-if='searchResults.length === 0'>
        <template v-if='!productNotFound'>
          <!-- Show loading or processing message -->
          Loading...
        </template>
        <template v-else>
          Product is not available
        </template>
      </div>

      <table class="table table-bordered table-striped" v-if="searchResults.length > 0">
        <thead class="thead-dark">
          <tr>
            <th>Product ID</th>
            <th>Product Name</th>
            <th>Category Name</th>
            <th>Rate Per Unit</th>
            <th>Available Quantity</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in searchResults" :key="result.Product_ID">
            <td>{{ result.Product_ID }}</td>
            <td>{{ result.Product_Name }}</td>
            <td>{{ result.Category_Name }}</td>
            <td>{{ result.Rate_Per_Unit }}</td>
            <td>{{ result.Available_Quantity }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
});

Vue.component('request_sender', {
  template: `
    <div>
      <h2>Request Sender</h2>
      <textarea v-model="requestText" placeholder="Write your request..."></textarea>
      <button @click="sendRequest">Send Request</button>
      <div>
        <p>Status: {{ status }}</p>
      </div>
    </div>
  `,
  
  data: function() {
    return {
      requestText: '',
      status: '',
    };
  },

  created: function() {
    // Fetch requests from the server when the component is created.
    this.fetchRequests();
  },

  methods: {

    sendRequestToServer: function(requestText) {
      return this.$http.post(`/app/send-request`, { request_text: requestText });
    },

    fetchRequestsFromServer: function() {
      return this.$http.get(`/app/fetch-requests`);
    },

    updateRequestStatus: function(requestId, status) {
      return this.$http.post(`/app/update-request-status/${requestId}/${status}`);
    },

    fetchRequests: function() {
      //Assume a function to fetch requests from the server
      //Using an HTTP GET request. This function should be implemented
      //in the main.js file
      this.fetchRequestsFromServer()
        .then(response => {
          this.requests = response.data;
        })
        .catch(error => {
          console.error(error);
        });
    },

    acceptRequest: function(requestId) {
      //Assume a function to update the status of a request to 'Accepted'
      //Using an HTTP POST request. The function should be implemented
      //in the main.js file.
      this.updateRequestStatus(requestId, 'Accepted');
    },

    rejectRequest: function(requestId) {
      //Assume a function to update the status of a request to 'Rejected'
      //Using an HTTP POST request. The function should be implemented
      //In the main.js file.
      this.udpateRequestStatus(requestId, 'Rejected');
    },

    sendRequest: function() {
      //Assume a function to send a request to the server
      //Using an HTTP POST request. This function should be implemented
      //In the main.js file
      this.sendRequestToServer(this.requestText)
        .then(response => {
          this.status = response.data.status;
        })
        .catch(error => {
          console.error(error);
        });
    },
  },
});

Vue.component('request-viewer', {
  template: `
    <div>
      <h2>Request Viewer</h2>
      <table class="table table-bordered table-striped">
        <thead class="thead-dark">
          <tr>
            <th>User ID</th>
            <th>Request</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in requests" :key="request.id">
            <td>{{ request.user_id }}</td>
            <td>{{ request.request_text }}</td>
            <td>{{ request.status }}</td>
            <td>
              <button @click="acceptRequest(request.id)">Accept</button>
              <button @click="rejectRequest(request.id)">Reject</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  `,

  data: function() {
    return {
      requests: [],
    };
  },

  created: function() {
    //Fetch requests from the server when the component is created.
    this.fetchRequests();
  },

  methods: {
    fetchRequestsFromServer: function() {
      return this.$http.get(`/app/fetch-requests`);
    },

    updateRequestStatus: function(requestId, status) {
      this.$http.post(`/app/update-request-status/${requestId}/${status}`)
        .then(response => {
          if(response.data.status === 'Request status updated successfully') {
            const updatedRequestIndex = this.requests.findIndex(request => request.id === requestId);
            if(updatedRequestIndex !== 1) {
              this.$set(this.requests, updatedRequestIndex, { ...this.requests[updatedRequestIndex], status });
            }
          }
        })
        .catch(error => {
          console.error(error);
        });
    },

    fetchRequests: function() {
      //Assume a function to fetch requests from the server
      //Using an HTTP GET request. This function should be implemented
      //In the main.js file
      this.fetchRequestsFromServer()
        .then(response => {
          this.requests = response.data;
        })
        .catch(error => {
          console.error(error);
        });
    },

    acceptRequest: function(requestId) {
      //Assume a function to update the status of a request to 'Accepted'
      //Using an HTTP POST request. This function should be implemented
      //in the main.js file.
      this.updateRequestStatus(requestId, 'Accepted');
    },

    rejectRequest: function(requestId) {
      //Assume a function to update the status of a request to 'Rejected'
      //Using an HTTP POST request. The function should be implemented
      //In the main.js file
      this.updateRequestStatus(requestId, 'Rejected');
    },
  },
});


// Initialize the Vue app
new Vue({
  el: '#app',
});