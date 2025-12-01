# Reusable Features Guide

This document provides a guide for developers on how to reuse the shared features implemented in this project. These features have been designed to be modular and easily integrated into other applications.

## 1. User Authentication

This feature provides a complete user login and registration system using Supabase for authentication.

### Overview

The authentication model is client-side. The frontend application communicates directly with Supabase to handle user registration and login, which returns a JWT. This token is then sent to the backend with each request to authenticate the user.

### Backend Implementation

- **JWT Verification:** The backend verifies the JWT token using the `get_current_user_id` and `get_current_user_id_optional` dependencies found in `src/backend/app/api/v1/dependencies/auth.py`. These functions use the `supabase-py` library to validate the token against the Supabase project.

### Frontend Implementation (Reusable Components)

The entire UI and client-side logic for authentication is available as a set of reusable components and services in `src/shared/auth/`.

- **Components:**
  - `LoginForm.tsx`: A complete login form component.
  - `RegistrationForm.tsx`: A complete registration form component.

- **Service:**
  - `authService.ts`: A centralized service that encapsulates all communication with Supabase. It handles login, registration, logout, and fetching the current user.

- **Types:**
  - `types/index.ts`: Contains shared TypeScript interfaces for `User`, `LoginCredentials`, etc.

### Libraries Used

- **Frontend:** `react`, `@supabase/supabase-js`
- **Backend:** `supabase-py`, `fastapi`

### How to Reuse

1.  **Copy the `src/shared/auth` directory** to your new application's shared components folder.
2.  **Install dependencies:** Make sure your `package.json` includes `react` and `@supabase/supabase-js`.
3.  **Configure Supabase Client:** The `authService` depends on a Supabase client instance. Ensure you have a Supabase client initialized in your application (e.g., in `src/lib/supabase/client.ts`) and that the import path in `authService.ts` is correct.
4.  **Use the Components:** Import and render the `LoginForm` or `RegistrationForm` components in your application's pages. Pass the required callback functions (`onLoginSuccess`, `onRegisterSuccess`) to handle the UI flow after authentication.

    ```jsx
    import LoginForm from '@/shared/auth/components/LoginForm';

    const MyLoginPage = () => {
      const handleLogin = () => {
        // Redirect user or update state
      };

      return <LoginForm onLoginSuccess={handleLogin} />;
    }
    ```

## 2. Token Usage Limits

This feature tracks and enforces daily and monthly token/cost usage limits for each user.

### Overview

The system tracks the number of requests and the total cost of LLM calls for each user on a daily and monthly basis. If a user exceeds their configured budget, they are blocked from making further requests until the period resets.

### Database Model

- **`UserUsage` Model:** The `src/shared/db/models/usage.py` file contains the `UserUsage` SQLAlchemy model. This table stores the daily and monthly costs and request counts for each user.

### Backend Implementation

- **`UsageService`:** The core logic is centralized in the `UsageService` class in `src/shared/usage/usage_service.py`. This service is asynchronous and designed to work with an `AsyncSession` from SQLAlchemy.
  - `check_limits(user)`: Checks if a user is within their budget.
  - `increment_usage(user_id, cost)`: Adds the cost of a request to the user's daily and monthly totals.
  - `reset_counters_if_needed(usage)`: Automatically resets the daily/monthly counters when a new period begins.

### Libraries Used

- **Backend:** `sqlalchemy`

### How to Reuse

1.  **Copy the `src/shared/usage` and `src/shared/db` directories** to your new backend application.
2.  **Integrate the Model:** Ensure the `UserUsage` model is imported and registered with your SQLAlchemy `Base` metadata.
3.  **Use the Service:** In your application's services (e.g., a `ChatService`), initialize the `UsageService` with a database session. Before processing a request that incurs a cost, call `await usage_service.check_limits(user)`. If it returns `False`, you should block the request (e.g., by raising an HTTP 429 Too Many Requests error). After a successful request, call `await usage_service.increment_usage(user.id, cost)`.

    ```python
    from src.shared.usage.usage_service import UsageService
    from fastapi import Depends, HTTPException, status

    async def process_request(user: User, db: AsyncSession = Depends(get_db)):
        usage_service = UsageService(db)
        if not await usage_service.check_limits(user):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)

        # ... process the request and calculate cost ...
        cost = 0.10 

        await usage_service.increment_usage(user.id, cost)
    ```

## 3. Cost Tracking & Analytics

This feature provides a centralized way to calculate the cost of LLM requests and a framework for building an analytics dashboard.

### Overview

Cost calculation is decoupled from individual LLM provider implementations. A central `CostCalculator` uses a shared pricing configuration file, making it easy to manage and update model costs.

### Pricing Configuration

- **`config/pricing.yaml`:** This file is the single source of truth for all model pricing. It defines the input and output cost per 1,000 tokens for each model.

### Backend Implementation

- **`ConfigLoader`:** The `get_pricing_data` method in `src/shared/config/config_loader.py` loads the `pricing.yaml` file.
- **`CostCalculator` Service:** The `src/shared/billing/cost_calculator.py` file contains the `CostCalculator` class. It loads the pricing data and provides a `calculate_cost(model, prompt_tokens, completion_tokens)` method.
- **`AnalyticsService` & Routes:** The `src/backend/app/services/analytics_service.py` and `src/backend/app/api/v1/routes/analytics.py` files provide a framework for creating API endpoints to expose usage and performance data.

### Frontend Implementation (Admin Dashboard)

- **`CostDashboard.tsx`:** A placeholder component exists in `src/admin-dashboard/src/components/analytics/` to serve as a starting point for a cost and usage analytics UI.

### Libraries Used

- **Backend:** `pyyaml`

### How to Reuse

1.  **Copy the `src/shared/billing` and `src/shared/config` directories** and the `config/pricing.yaml` file to your new application.
2.  **Use the `CostCalculator`:** In any service that needs to calculate the cost of an LLM call, instantiate the `CostCalculator` and call the `calculate_cost` method.

    ```python
    from src.shared.billing.cost_calculator import CostCalculator

    cost_calculator = CostCalculator()
    cost = cost_calculator.calculate_cost(
        model="claude-3-sonnet", 
        prompt_tokens=1000, 
        completion_tokens=500
    )
    ```
4.  **Build Analytics UI:** The `src/admin-dashboard` can be used as a template for building a full-featured analytics interface that consumes the data from the `/api/v1/analytics` endpoints.

## 4. LLM Provider Integration

This feature provides a unified interface for communicating with multiple LLM providers, with automatic fallback and provider selection.

### Overview

The `UnifiedLLMProvider` service acts as a single entry point for making LLM calls. It can route requests to different providers like OpenRouter and LM Studio based on availability and user preference.

### Backend Implementation

- **Provider Services:** The `src/shared/llm_providers` directory contains the provider implementations:
  - `unified_llm_provider.py`: The main orchestrator.
  - `openrouter_provider.py`: Integration for the OpenRouter API.
  - `lm_studio_provider.py`: Integration for a local LM Studio instance.

### Libraries Used

- **Backend:** `httpx`

### How to Reuse

1.  **Copy the `src/shared/llm_providers` directory** to your new backend application.
2.  **Use the `UnifiedLLMProvider`:** In your application's services, instantiate the `UnifiedLLMProvider` and use its `call_model` method to make LLM requests.

    ```python
    from src.shared.llm_providers.unified_llm_provider import UnifiedLLMProvider
    from app.models.schemas import LLMRequest

    llm_provider = UnifiedLLMProvider()
    request = LLMRequest(model="claude-3-sonnet", user_message="Hello, world!")
    response = await llm_provider.call_model(request)
    ```

## 5. Core UI Component Library

This feature provides a set of generic and reusable UI components.

### Overview

A collection of basic UI components are available in the `src/shared/ui` directory. These can be used to build a consistent user interface across multiple applications.

### Components

- `Button.tsx`: A flexible button component with primary, secondary, and danger variants.
- `Modal.tsx`: A simple modal dialog component.
- `LanguageSelector.tsx`: A dropdown for selecting a language (Note: This component is currently tailored for Next.js with `next-intl` but can be adapted).

### Libraries Used

- **Frontend:** `react`

### How to Reuse

1.  **Copy the `src/shared/ui` directory** to your new application's shared components folder.
2.  **Import and use the components** in your application's pages and other components.

    ```jsx
    import Button from '@/shared/ui/Button';
    import Modal from '@/shared/ui/Modal';

    const MyComponent = () => {
      // ...
      return <Button>Click me</Button>;
    }
    ```

## 6. Centralized Configuration Loader

This feature provides a utility for loading configuration from YAML files.

### Overview

The `ConfigLoader` class provides a simple way to load and cache configuration from YAML files located in a central `config` directory.

### Backend Implementation

- **`ConfigLoader`:** The `src/shared/config/config_loader.py` file contains the `ConfigLoader` class.

### Libraries Used

- **Backend:** `pyyaml`

### How to Reuse

1.  **Copy the `src/shared/config` directory** to your new backend application.
2.  **Create a `config` directory** in your project root and add your YAML configuration files there.
3.  **Use the `get_config_loader` function** to get an instance of the `ConfigLoader` and then call its methods to retrieve your configuration data.

    ```python
    from src.shared.config.config_loader import get_config_loader

    config_loader = get_config_loader()
    my_config = config_loader._load_yaml("my_config.yaml")
    ```