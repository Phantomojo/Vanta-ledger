# VantaLedger Android App - UI/UX Guidelines

## Design Philosophy

VantaLedger combines the professional financial interface of MPesa with the engaging timeline feel of Instagram to create a modern, intuitive financial management experience. The design prioritizes clarity, ease of use, and visual appeal.

## Design Principles

1. **Clarity First**: Financial information must be immediately understandable
2. **Consistent Visual Language**: Maintain consistent patterns throughout the app
3. **Purposeful Animation**: Use motion to enhance understanding, not distract
4. **Accessible Design**: Ensure the app is usable by people with diverse abilities
5. **Glanceable Information**: Key financial data should be visible at a glance

## Color System

### Primary Colors
- **Primary**: `#1E88E5` (MPesa Blue) - Main brand color
- **Secondary**: `#26A69A` (Mint Green) - Accent color for positive actions
- **Error**: `#E53935` (Coral Red) - For errors and negative balances

### Semantic Colors
- **Income**: `#43A047` (Green) - For income transactions
- **Expense**: `#E53935` (Red) - For expense transactions
- **Neutral**: `#757575` (Gray) - For informational elements

### Background Colors
- **Light Theme Background**: `#FFFFFF` (White)
- **Dark Theme Background**: `#121212` (Dark Gray)
- **Surface Light**: `#F5F5F5` (Light Gray)
- **Surface Dark**: `#1E1E1E` (Charcoal)

## Typography

### Font Family
- **Primary Font**: Roboto (System default)
- **Alternative**: Inter or SF Pro (if available)

### Type Scale
- **Display Large**: 32sp - App title, splash screen
- **Display Medium**: 28sp - Screen titles
- **Display Small**: 24sp - Major section headers
- **Headline**: 20sp - Card titles, important numbers
- **Title**: 16sp - Section headers
- **Body**: 14sp - General text, transaction descriptions
- **Caption**: 12sp - Supporting text, dates, labels

## Component Guidelines

### Cards
- Use cards to group related information
- Maintain consistent padding (16dp)
- Include clear headers
- Use subtle shadows for elevation (2dp standard)
- Round corners (8dp radius)

### Buttons
- **Primary Action**: Filled button with brand color
- **Secondary Action**: Outlined button
- **Tertiary Action**: Text button
- Use consistent padding (16dp horizontal, 8dp vertical)
- Include icons when helpful for recognition

### Icons
- Use Material Design icons as a base
- Customize key financial icons for brand recognition
- Maintain consistent size (24dp standard)
- Use color to indicate state or category

### Lists
- Use dividers or subtle shadows to separate items
- Consistent padding (16dp)
- Include visual indicators for different transaction types
- Support swipe actions for common operations

## Screen Templates

### Timeline/Feed (Instagram-inspired)
- Chronological list of transactions
- Card-based design for each transaction
- Pull-to-refresh functionality
- Infinite scrolling with date headers
- Quick action buttons

### Dashboard (MPesa-inspired)
- Prominent balance display
- Quick action buttons for common tasks
- Recent transactions preview
- Budget status indicators
- Visual charts for spending breakdown

### Detail Screens
- Full information display
- Edit/delete actions
- Related information (e.g., category breakdown)
- Back navigation consistent with Android patterns

### Form Screens
- Clear labels
- Inline validation
- Keyboard optimization
- Progressive disclosure for advanced options

## Animation Guidelines

### Transitions
- Use standard Material motion patterns
- Container transforms for related elements
- Shared element transitions for detail views
- Duration: 300ms standard

### Feedback Animations
- Subtle scale or color changes for button presses
- Progress indicators for operations
- Success/error animations for confirmations

### Chart Animations
- Animate chart data changes (500ms)
- Use easing functions for natural movement
- Sequence complex animations

## Accessibility Guidelines

### Color Contrast
- Maintain minimum 4.5:1 contrast ratio for text
- Don't rely solely on color to convey information
- Test with color blindness simulators

### Touch Targets
- Minimum 48dp x 48dp for interactive elements
- Adequate spacing between touchable items (8dp minimum)

### Screen Readers
- Meaningful content descriptions for all UI elements
- Logical navigation order
- Announce dynamic content changes

### Text Scaling
- Support font scaling up to 200%
- Test layouts with larger text sizes
- Avoid fixed-size containers for text

## Responsive Design

### Screen Sizes
- Design for phones first (360dp - 420dp width)
- Support larger phones and small tablets (600dp+)
- Adjust layouts for landscape orientation

### Adaptive Layouts
- Single column on phones
- Consider multi-column layouts on larger screens
- Maintain consistent padding and spacing

## Dark Mode

- True black backgrounds for OLED screens
- Reduce brightness of imagery
- Maintain color semantics (income still green, expenses still red)
- Test all screens in both light and dark modes
