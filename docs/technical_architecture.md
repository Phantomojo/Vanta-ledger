# VantaLedger Android App - Technical Architecture

## Overview

The VantaLedger Android app follows the MVVM (Model-View-ViewModel) architecture pattern with a clean architecture approach. This document outlines the technical architecture of the application, including the data flow, component responsibilities, and key technologies.

## Architecture Layers

### 1. Presentation Layer

The presentation layer is responsible for displaying data to the user and handling user interactions.

#### Components:
- **Composables**: UI components built with Jetpack Compose
- **ViewModels**: Manage UI state and business logic
- **UI States**: Immutable data classes representing screen states
- **Navigation**: Compose Navigation component for screen transitions

#### Technologies:
- Jetpack Compose
- Compose Navigation
- ViewModel
- LiveData/StateFlow

### 2. Domain Layer

The domain layer contains the business logic and rules of the application.

#### Components:
- **Use Cases**: Single-responsibility classes for business operations
- **Domain Models**: Core business models independent of data sources
- **Repositories Interfaces**: Abstractions for data operations

#### Technologies:
- Kotlin Coroutines
- Flow

### 3. Data Layer

The data layer is responsible for data retrieval, storage, and manipulation.

#### Components:
- **Repositories**: Implementations of repository interfaces
- **Data Sources**: Local (Room) and remote (if applicable) data sources
- **Data Models**: Database entities and DTOs
- **DAOs**: Data Access Objects for database operations

#### Technologies:
- Room Database
- SQLite
- Retrofit (for potential future API integration)
- DataStore (for preferences)

## Data Flow

1. **UI Layer**: User interacts with Composables
2. **ViewModel**: Processes UI events and updates UI state
3. **Use Cases**: Execute business logic
4. **Repositories**: Coordinate data operations
5. **Data Sources**: Perform actual data operations
6. **Back to UI**: Data flows back up through the layers

## Key Components

### Room Database

```kotlin
@Database(
    entities = [
        Transaction::class,
        Category::class,
        Budget::class,
        RecurringTransaction::class,
        Account::class
    ],
    version = 1
)
abstract class VantaLedgerDatabase : RoomDatabase() {
    abstract fun transactionDao(): TransactionDao
    abstract fun categoryDao(): CategoryDao
    abstract fun budgetDao(): BudgetDao
    abstract fun recurringTransactionDao(): RecurringTransactionDao
    abstract fun accountDao(): AccountDao
}
```

### Dependency Injection

The app uses Hilt for dependency injection to provide dependencies to various components.

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): VantaLedgerDatabase {
        return Room.databaseBuilder(
            context,
            VantaLedgerDatabase::class.java,
            "vanta_ledger.db"
        ).build()
    }
    
    @Provides
    @Singleton
    fun provideTransactionRepository(
        database: VantaLedgerDatabase
    ): TransactionRepository {
        return TransactionRepositoryImpl(database.transactionDao())
    }
    
    // Other providers...
}
```

### ViewModels

```kotlin
@HiltViewModel
class TransactionViewModel @Inject constructor(
    private val getTransactionsUseCase: GetTransactionsUseCase,
    private val addTransactionUseCase: AddTransactionUseCase,
    private val deleteTransactionUseCase: DeleteTransactionUseCase
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(TransactionUiState())
    val uiState: StateFlow<TransactionUiState> = _uiState.asStateFlow()
    
    init {
        loadTransactions()
    }
    
    private fun loadTransactions() {
        viewModelScope.launch {
            getTransactionsUseCase().collect { transactions ->
                _uiState.update { it.copy(
                    transactions = transactions,
                    isLoading = false
                ) }
            }
        }
    }
    
    // Other methods...
}
```

### Composables

```kotlin
@Composable
fun TransactionScreen(
    viewModel: TransactionViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column {
        // UI components
    }
}
```

## Navigation

The app uses Compose Navigation for screen transitions.

```kotlin
@Composable
fun VantaLedgerNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = "home",
        modifier = modifier
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToTransactions = { navController.navigate("transactions") }
            )
        }
        composable("transactions") {
            TransactionScreen()
        }
        // Other destinations...
    }
}
```

## Error Handling

The app implements a comprehensive error handling strategy:

1. **UI Layer**: Display user-friendly error messages
2. **ViewModel**: Capture and transform errors into UI states
3. **Use Cases**: Handle business logic errors
4. **Repositories**: Handle data operation errors
5. **Global Error Handler**: Capture uncaught exceptions

## Testing Strategy

### Unit Tests

```kotlin
@Test
fun `when adding transaction, repository should be called`() = runTest {
    // Given
    val transaction = Transaction(amount = 100.0, type = "expense")
    
    // When
    addTransactionUseCase(transaction)
    
    // Then
    verify(repository).addTransaction(transaction)
}
```

### UI Tests

```kotlin
@Test
fun transactionScreen_displaysTransactions() {
    // Given
    val transactions = listOf(
        Transaction(id = 1, amount = 100.0, type = "expense"),
        Transaction(id = 2, amount = 200.0, type = "income")
    )
    
    // When
    composeTestRule.setContent {
        TransactionScreen(
            viewModel = FakeTransactionViewModel(transactions)
        )
    }
    
    // Then
    transactions.forEach { transaction ->
        composeTestRule.onNodeWithText("$${transaction.amount}").assertIsDisplayed()
    }
}
```

## Performance Considerations

1. **Paging**: Use Paging 3 library for large lists
2. **Background Processing**: Use WorkManager for long-running tasks
3. **Efficient Database Queries**: Optimize Room queries
4. **Lazy Loading**: Load data only when needed
5. **Composition Optimization**: Minimize recompositions in Compose

## Security Measures

1. **Encrypted Database**: Use SQLCipher for database encryption
2. **Secure Preferences**: Use EncryptedSharedPreferences
3. **Biometric Authentication**: Implement BiometricPrompt
4. **Data Validation**: Validate all user inputs
5. **Secure Backup**: Encrypt backup files
