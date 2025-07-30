# React Framework Guide

## Overview
React is a declarative, efficient, and flexible JavaScript library for building user interfaces. It lets you compose complex UIs from small, isolated pieces of code called "components". This guide covers React best practices and patterns used in Windsurf projects.

## Key Features
- **Component-Based**: Build encapsulated components that manage their own state
- **Declarative**: Design simple views for each state in your application
- **Learn Once, Write Anywhere**: Can render on the server using Node and power mobile apps using React Native
- **Rich Ecosystem**: Large community and extensive packagecosystem
- **Performance**: Virtual DOM ensures efficient updates and rendering

## Installation

### Using Create React App (Recommended)

```bash
# Create a new React applicationpx create-react-app my-app --template typescript

# Navigate to the project directory
cd my-app

# Starthe development server
npm start
```

### Manual Setup

```bash
# Install React and React DOM
npm install react-dom

# For TypeScript support
npm install --save-dev typescript @types/react @types/react-dom
```

## Project Structure

```
my-react-app/
├── public/                 # Static files
│   ├── index.html          # Main HTML file
│   └── favicon.ico         # Favicon
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.module.css
│   │   │   └── index.ts
│   │   └── ...
│   ├── pages/              # Page components
│   │   ├── Home/
│   │   └── ...
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   ├── store/              # State management
│   ├── types/              # TypeScriptype definitions
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main App component
│   ├── index.tsx           # Application entry point
│   └── index.css           # Global styles
├── .eslintrc.js            # ESLint configuration
├── .prettierrc             # Prettier configuration
├── tsconfig.json           # TypeScript configuration
├── package.json
└── README.md
```

## Core Concepts

### Functional Components

```tsx
// components/Greeting.tsx
import React from 'react';

interface GreetingProps {
  name: string;
  age?: number;
}

const Greeting: React.FC<GreetingProps> = ({ name, age }) => {
  return (
    <div className="greeting">
      <h1>Hello, {name}!</h1>
      {age && <p>You are {age} years old.</p>}
    </div>
  );
};

export default Greeting;
```

### Hooks

#### useState

```tsx
import { useState } from 'react';

const Counter = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <buttonClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
};
```

#### useEffect

```tsx
import { useState, useEffect } from 'react';

const DataFetcher = ({ userId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]); // Re-run when userId changes

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  return <div>{JSON.stringify(data, null, 2)}</div>;
};
```

#### Custom Hooks

```tsx
// hooks/useLocalStorage.ts
import { useState, useEffect } from 'react';

const useLocalStorage = (key: string, initialValue: any) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: any) => {
    try {
      const valueToStore = value instanceofunction ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
};

export default useLocalStorage;
```

## State Management

### Context API

```tsx
// context/ThemeContext.tsx
import React, { createContext, useContext, useState } from 'react';

type Theme = 'light' | 'dark';

type ThemeContextType = {
  theme: Theme;
  toggleTheme: () => void;
};

consthemeContext = createContext<ThemeContextType | undefined>(undefined);

export consthemeProvider: React.FC = ({ children }) => {
  const [theme, setTheme] = useState<Theme>('light');

  constoggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className={`app ${theme}`}>{children}</div>
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
```

### Redux Toolkit (Recommended for complex state)

```bash
# Install Redux Toolkit
npm install @reduxjs/toolkit react-redux
```

```tsx
// store/slices/counterSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CounterState {
  value: number;
}

const initialState: CounterState = {
  value: 0,
};

const counterSlice = createSlice({
  name: 'counter',
  initialState,
  reducers: {
    incremented: state => {
      state.value += 1;
    },
    decremented: state => {
      state.value -= 1;
    },
    amountAdded: (state, action: PayloadAction<number>) => {
      state.value += action.payload;
    },
  },
});

export const { incremented, decremented, amountAdded } = counterSlice.actions;
export default counterSlice.reducer;
```

## Styling

### CSS Modules

```css
/* Button.module.css */
.button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.button:hover {
  background-color: #0056b3;
}

/* Component usage */
import styles from './Button.module.css';

const Button = () => (
  <button className={styles.button}>Click me</button>
);
```

### Styled Components

```bash
# Install styled-components
npm install styled-components @types/styled-components
```

```tsx
import styled from 'styled-components';

constyledButton = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: ${props => props.primary ? '#007bff' : '#6c757d'};
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: ${props => props.primary ? '#0056b3' : '#5a6268'};
  }
`;

// Usage
<StyledButton primary>Primary Button</StyledButton>
<StyledButton>Secondary Button</StyledButton>
```

## Testing

### Jest and Reactesting Library

```bash
# Install testing libraries
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

```tsx
// Button.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Button from './Button';

describe('Button', () => {
  it('renders the button with correctext', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick prop when clicked', () => {
    const handleClick = jest.fn();
    render(<ButtonClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText(/click me/i));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## Performance Optimization

### React.memo

```tsx
import { memo } from 'react';

interface UserCardProps {
  id: number;
  name: string;
  email: string;
  onEdit: (id: number) => void;
}

const UserCard: React.FC<UserCardProps> = memo(({ id, name, email, onEdit }) => {
  console.log(`Rendering UserCard ${id}`);
  
  return (
    <div className="user-card">
      <h3>{name}</h3>
      <p>{email}</p>
      <buttonClick={() => onEdit(id)}>Edit</button>
    </div>
  );
}, (prevProps, nextProps) => {
  // Only re-render if these props change
  return (
    prevProps.id === nextProps.id &&
    prevProps.name === nextProps.name &&
    prevProps.email === nextProps.email
  );
});

export default UserCard;
```

### useCallback and useMemo

```tsx
import { useCallback, useMemo, useState } from 'react';

const ExpensiveComponent = ({ items, onItemClick }) => {
  // Only recalculate when items change
  const sortedItems = useMemo(() => {
    console.log('Sorting items...');
    return [...items].sort((a, b) => a.value - b.value);
  }, [items]);

  // Memoize the callback function
  const handleClick = useCallback((item) => {
    onItemClick(item.id);
  }, [onItemClick]);

  return (
    <ul>
      {sortedItems.map(item => (
        <li key={item.id} onClick={() => handleClick(item)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
};
```

## Best Practices

1. **Component Design**
   - Keep componentsmall and focused
   - Use composition over inheritance
   - Follow the single responsibility principle

2. **State Management**
   - Use local state for UI state
   - Lift state up wheneeded
   - Consider context for global state
   - Use Redux for complex state management

3. **Performance**
   - Use React.memo for expensive renders
   - Memoize callbacks with useCallback
   - Memoizexpensive calculations with useMemo
   - Lazy load components with React.lazy

4. **Testing**
   - Write unitests for components
   - Test user interactions
   - Use Reactesting Library

5. **Code Organization**
   - Group by feature oroute
   - Keep related files together
   - Use index files for clean imports

## Resources

- [Official Documentation](https://reactjs.org/)
- [ReactypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [React Patterns](https://reactpatterns.com/)
- [Reactesting Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Redux Toolkit](https://redux-toolkit.js.org/)

## Last Updated
2025-06-23
