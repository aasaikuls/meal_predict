#### Original Reference file ... Currently not in use
##Mains logics that are used from here are
'''

1. _get_restricted_probabilities()
Note: _get_restricted_probabilities_with_weekday() --> note have change this in main.py use. 

2. process_passengers(self, passenger_df: pd.DataFrame) --> this where the main probability X weights happen. 
 Though the purpose of this function is the same, the way the logic is used and rendered is different in main.py Here it is processing whole csv. In main.py it is looking at individual flights and dates.

'''



import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class MealPlanningSystem:
    def __init__(self, 
                 meal_df_path: str,
                 nationality_weights_path: str,
                 age_weights_path: str,
                 destination_weights_path: str,
                 mealtime_weights_path: str):
        
        # Load weight data
        self.nationality_w = pd.read_csv(nationality_weights_path)
        self.age_w = pd.read_csv(age_weights_path)
        self.destination_w = pd.read_csv(destination_weights_path)
        self.mealtime_w = pd.read_csv(mealtime_weights_path)
        
        # Load meal data
        self.meal_df = pd.read_excel(meal_df_path)
        ## change dt format to match customer df
        self.meal_df['segment_local_departure_date'] = pd.to_datetime(self.meal_df['segment_local_departure_date']).dt.date
        
        # Extract unique destination regions
        self.destination_regions_unique = self.destination_w[['destination_region', 'Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']].drop_duplicates()
        
        # Feature weights
        self.W1 = 0.40  # Nationality
        self.W2 = 0.20  # Age Group
        self.W3 = 0.25  # Destination
        self.W4 = 0.15  # Meal Time
        
    def _get_restricted_probabilities(self, feature_value: str, weight_df: pd.DataFrame, feature_column: str, available_proteins: List[str]) -> Dict[str, float]:

        # Get the row for this feature value...in the weight_df 
        feature_row = weight_df[weight_df[feature_column] == feature_value]
        
        if feature_row.empty:
            # Return equal probabilities if feature not found
            equal_prob = 1.0 / len(available_proteins)
            return {protein: equal_prob for protein in available_proteins}
        
        protein_columns = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']
        available_probs = {}
        total_prob = 0
        
        for protein in available_proteins:
            if protein in protein_columns:
                prob = feature_row[protein].iloc[0]
                available_probs[protein] = prob
                total_prob += prob
        
        # Normalize probabilities to sum to 1
        if total_prob > 0:
            normalized_probs = {
                protein: prob/total_prob 
                for protein, prob in available_probs.items()
            }
        else:
            equal_prob = 1.0 / len(available_proteins)
            normalized_probs = {protein: equal_prob for protein in available_proteins}
        
        return normalized_probs
    
    def _get_restricted_probabilities_with_weekday(self,
                                                   nationality_code: str,
                                                   weekday: str,
                                                   available_proteins: List[str]) -> Dict[str, float]:
        
        feature_row = self.nationality_w[(self.nationality_w['nationality_code'] == nationality_code) & (self.nationality_w['day_of_week'] == weekday)]
        
        if feature_row.empty:
            equal_prob = 1.0 / len(available_proteins)
            return {protein: equal_prob for protein in available_proteins}
        
        protein_columns = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']
        available_probs = {}
        total_prob = 0
        
        for protein in available_proteins:
            if protein in protein_columns:
                prob = feature_row[protein].iloc[0]
                available_probs[protein] = prob
                total_prob += prob
        
        if total_prob > 0:
            normalized_probs = {
                protein: prob/total_prob 
                for protein, prob in available_probs.items()
            }
        else:
            equal_prob = 1.0 / len(available_proteins)
            normalized_probs = {protein: equal_prob for protein in available_proteins}
        
        return normalized_probs
    
    def _get_meal_info(self, segment: str,cabin_class: str,date,meal_time: str) -> Tuple[List[Dict], List[str]]:
        """
        Get available meals and proteins for a specific flight segment.  
        Returns:Tuple of (meal_info_list, protein_list)
        """
        matching_meals = self.meal_df[
            (self.meal_df['segment'] == segment) & 
            (self.meal_df['cabin_class'] == cabin_class) & 
            (self.meal_df['segment_local_departure_date'] == date) & 
            (self.meal_df['meal_time'] == meal_time)
        ]
        
        if matching_meals.empty:
            return [], []
        
        meal_info_list = []
        protein_list = []
        
        for _, meal_row in matching_meals.iterrows():
            meal_dict = {
                "meal_name": meal_row['meal_name'],
                "protein": meal_row['meal_pref']
            }
            meal_info_list.append(meal_dict)
            protein_list.append(meal_row['meal_pref'])
        
        return meal_info_list, protein_list
    
    def _calculate_protein_counts(self,passenger_count: int,final_protein_probs: Dict[str, float],available_proteins: List[str]) -> Dict[str, Dict]:
        """
        Calculate final passenger counts per protein using largest remainder method.
        
        Args:
            passenger_count: Total number of passengers
            final_protein_probs: Final probabilities for each protein
            available_proteins: List of available proteins
            
        Returns:
            Dictionary with protein counts and probabilities
        """
        protein_counts = {}
        remainders = {}
        
        # Calculate exact counts and floor them
        for protein in available_proteins:
            count_exact = passenger_count * final_protein_probs[protein]
            floor_count = int(count_exact)
            remainder = count_exact - floor_count
            
            protein_counts[protein] = {
                'probability': round(final_protein_probs[protein], 4),
                'count_exact': round(count_exact, 2),
                'count_final': floor_count
            }
            remainders[protein] = remainder
        
        # Distribute remaining passengers
        total_allocated = sum([protein_counts[p]['count_final'] for p in available_proteins])
        remaining_passengers = passenger_count - total_allocated
        
        if remaining_passengers > 0:
            sorted_proteins = sorted(
                available_proteins, 
                key=lambda p: remainders[p], 
                reverse=True
            )
            
            for i in range(min(remaining_passengers, len(sorted_proteins))):
                protein = sorted_proteins[i]
                protein_counts[protein]['count_final'] += 1
        
        return protein_counts
    
    def process_passengers(self, passenger_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process passenger data and calculate meal distribution.
        Args: passenger_df: DataFrame with passenger information
        Returns:Transposed DataFrame with meal counts per flight
        """
        # Clean and prepare data
        df = passenger_df.copy()
        
        # Remove under 2 age group if present
        if 'age_group' in df.columns:
            df = df[df.age_group != 'Under 2']

        ###### Y class and S class passengers #############
        flights_4 =  df[(df.segment != 'SIN JFK') & (df.cabin_class == 'Y')]
        flight_jfk = df[(df.segment == "SIN JFK")&(df.cabin_class == 'S')]
        df = pd.concat([flights_4, flight_jfk], axis = 0, ignore_index = True)
        
        # Fix age group format
        if 'age_group' in df.columns:
            df['age_group'] = df['age_group'].replace("Feb-18", "2-18")
        
        # Convert datetime
        df['segment_local_departure_datetime'] = pd.to_datetime(df['segment_local_departure_datetime'], dayfirst=True)
        df['segment_local_departure_date'] = df['segment_local_departure_datetime'].dt.date
        df['weekday'] = df['segment_local_departure_datetime'].dt.day_name()
        
        # Merge destination region
        df = df.merge(
            self.destination_w[['airport_code', 'destination_region']], 
            left_on='arrival_airport',  
            right_on='airport_code', 
            how='left'
        )
        
        # Create feature sets
        df['feature_set'] = (
            df['nationality_code'] + '_' + 
            df['age_group'] + '_' + 
            df['destination_region'] + '_' + 
            df['meal_time']
        )
        
        # Group by features
        daily_feature_counts = df.groupby([
            'segment', 'cabin_class', 'segment_local_departure_date', 
            'weekday', 'feature_set'
        ]).size().reset_index(name='passenger_count')
        
        # Get feature details
        feature_details = df.groupby('feature_set').agg({
            'nationality_code': 'first',
            'age_group': 'first',
            'destination_region': 'first',
            'meal_time': 'first'
        }).reset_index()
        
        daily_feature_counts = daily_feature_counts.merge(
            feature_details, 
            on='feature_set', 
            how='left'
        )
        
        # Get available meals in each feature griup
        daily_feature_counts[['meals_available', 'proteins_available']] = (
            daily_feature_counts.apply(
                lambda row: pd.Series(self._get_meal_info(
                    row['segment'], 
                    row['cabin_class'], 
                    row['segment_local_departure_date'], 
                    row['meal_time']
                )), axis=1
            )
        )
        
        # calculate final probabilities and counts
        final_results = []
        
        for idx, row in daily_feature_counts.iterrows():
            available_proteins = row['proteins_available']
            
            if not available_proteins or len(available_proteins) == 0:
                continue
            
            # Get normalized probabilities for each feature
            nat_probs = self._get_restricted_probabilities_with_weekday(
                row['nationality_code'], 
                row['weekday'], 
                available_proteins
            )
            age_probs = self._get_restricted_probabilities(
                row['age_group'], 
                self.age_w, 
                'age_group', 
                available_proteins
            )
            dest_probs = self._get_restricted_probabilities(
                row['destination_region'], 
                self.destination_regions_unique, 
                'destination_region', 
                available_proteins
            )
            meal_probs = self._get_restricted_probabilities(
                row['meal_time'], 
                self.mealtime_w, 
                'meal_time', 
                available_proteins
            )
            
            # Calculate weighted probabilities
            weighted_protein_probs = {}
            for protein in available_proteins:
                weighted_prob = (
                    nat_probs.get(protein, 0) * self.W1 + 
                    age_probs.get(protein, 0) * self.W2 + 
                    dest_probs.get(protein, 0) * self.W3 + 
                    meal_probs.get(protein, 0) * self.W4
                )
                weighted_protein_probs[protein] = weighted_prob
            
            # Normalize final probabilities
            total_final_prob = sum(weighted_protein_probs.values())
            if total_final_prob > 0:
                final_protein_probs = {
                    protein: prob/total_final_prob 
                    for protein, prob in weighted_protein_probs.items()
                }
            else:
                equal_prob = 1.0 / len(available_proteins)
                final_protein_probs = {
                    protein: equal_prob 
                    for protein in available_proteins
                }
            
            # Calculate passenger counts
            protein_counts = self._calculate_protein_counts(
                row['passenger_count'],
                final_protein_probs,
                available_proteins
            )
            
            # Create result dictionary
            result_dict = {
                'segment': row['segment'],
                'cabin_class': row['cabin_class'],
                'segment_local_departure_date': row['segment_local_departure_date'],
                'weekday': row['weekday'],
                'meal_time': row['meal_time'],
                'passenger_count': row['passenger_count'],
                'meals_available': row['meals_available']
            }
            
            # Add protein counts
            for protein in available_proteins:
                result_dict[f'{protein.lower()}_count_final'] = (
                    protein_counts[protein]['count_final']
                )
            
            final_results.append(result_dict)
        
        final_results_df = pd.DataFrame(final_results)
        
        # Aggregate by flight
        aggregated_results = self._aggregate_results(final_results_df)
        
        # Transpose to meal-level view
        transposed_df = self._transpose_results(aggregated_results)
        
        return transposed_df
    
    def _aggregate_results(self, final_results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate results by flight segment.
        Args:final_results_df: DataFrame with feature-level results
        Returns:Aggregated DataFrame by flight
        """

        print("AGGREGATING THE RESULTS!!!!!!")

        protein_count_columns = [
            col for col in final_results_df.columns 
            if col.endswith('_count_final')
        ]
        
        agg_dict = {col: 'sum' for col in protein_count_columns}
        agg_dict['passenger_count'] = 'sum'
        
        aggregated_results = final_results_df.groupby([
            'segment', 
            'cabin_class', 
            'segment_local_departure_date', 
            'weekday',
            'meal_time'
        ]).agg(agg_dict).reset_index()
        
        # Get meals_available
        meals_available_df = final_results_df.groupby([
            'segment', 
            'cabin_class', 
            'segment_local_departure_date',
            'weekday',
            'meal_time'
        ])['meals_available'].first().reset_index()
        
        aggregated_results = aggregated_results.merge(
            meals_available_df, 
            on=['segment', 'cabin_class', 'segment_local_departure_date', 
                'weekday', 'meal_time'],
            how='left'
        )
        
        return aggregated_results
    
    def _transpose_results(self, aggregated_results: pd.DataFrame) -> pd.DataFrame:
        """
        Transpose results to meal-level view.
        Args:aggregated_results: Aggregated results by flight
        Returns:Transposed DataFrame with one row per meal
        """
        print("TRANSPOSING THE RESULTS!!!!!!")
        transposed_results = []
        
        for idx, row in aggregated_results.iterrows():
            meals_available = row['meals_available']
            total_passengers = row['passenger_count']
            
            # Get protein counts
            protein_counts = {}
            for col in aggregated_results.columns:
                if col.endswith('_count_final'):
                    protein_type = col.replace('_count_final', '').title()
                    count = row[col]
                    if count > 0:
                        protein_counts[protein_type] = count
            
            # Create row for each meal
            for meal_info in meals_available:
                meal_name = meal_info['meal_name']
                meal_protein = meal_info['protein'].title()
                
                count = protein_counts.get(meal_protein, 0)
                percentage = (
                    round((count / total_passengers) * 100, 2) 
                    if total_passengers > 0 and count > 0 
                    else 0
                )
                
                # Check if protein type appears multiple times
                protein_meal_count = sum(
                    1 for meal in meals_available 
                    if meal['protein'].title() == meal_protein
                )
                protein_repeated = protein_meal_count > 1
                
                transposed_results.append({
                    'segment': row['segment'],
                    'cabin_class': row['cabin_class'],
                    'segment_local_departure_date': row['segment_local_departure_date'],
                    'weekday': row['weekday'],
                    'meal_time': row['meal_time'],
                    'passenger_count': row['passenger_count'],
                    'meal_name': meal_name,
                    'protein_type': meal_protein,
                    'count': count,
                    'percentage': percentage,
                    'protein_repeated': protein_repeated
                })
        
        transposed_df = pd.DataFrame(transposed_results)
        
        return transposed_df


def calculate_meal_distribution(passenger_df: pd.DataFrame,
                               meal_df_path: str,
                               nationality_weights_path: str,
                               age_weights_path: str,
                               destination_weights_path: str,
                               mealtime_weights_path: str) -> pd.DataFrame:
    """
    Main function to calculate meal distribution for flights.
        
    Returns:
        DataFrame with meal counts per flight (transposed view)
        Columns:
            - segment, cabin_class, segment_local_departure_date, weekday, meal_time
            - passenger_count: Total passengers
            - meal_name: Name of the meal
            - protein_type: Protein type
            - count: Number of meals needed
            - percentage: Percentage of total passengers
            - protein_repeated: Whether protein appears in multiple meals
    """
    print("Have started to run the meal planning system code!")

    system = MealPlanningSystem(
        meal_df_path=meal_df_path,
        nationality_weights_path=nationality_weights_path,
        age_weights_path=age_weights_path,
        destination_weights_path=destination_weights_path,
        mealtime_weights_path=mealtime_weights_path
    )
    
    return system.process_passengers(passenger_df)


if __name__ == "__main__":
    # Load passenger data
    passenger_data = pd.read_csv(
        r"C:\Users\9SHRIDA_SUMANTH\OneDrive - Singapore Airlines Limited\Desktop\Meal Prediction\Weightage Method Code\Weightage For All Flights\Data\customers.csv",
        dtype={'age_group': str}, 
        low_memory=False
    )
    
    # Define paths to weight files
    meal_df_path = r"C:\Users\9SHRIDA_SUMANTH\OneDrive - Singapore Airlines Limited\Desktop\Meal Prediction\Weightage Method Code\Weightage For All Flights\Code\meal_df_new.xlsx"
    nationality_weights_path = r"C:\Users\9SHRIDA_SUMANTH\OneDrive - Singapore Airlines Limited\Desktop\Meal Prediction\Weightage Method Code\Weightage For All Flights\Data\Claude\nationality_meal_preferences_by_day_FRESH_CLAUDE.csv"
    age_weights_path = r"C:\Users\9SHRIDA_SUMANTH\OneDrive - Singapore Airlines Limited\Desktop\Meal Prediction\Weightage Method Code\Weightage For All Flights\Data\Claude\age_group_meal_preferences_with_sources.csv"
    destination_weights_path = r"C:\Users\9SHRIDA_SUMANTH\OneDrive - Singapore Airlines Limited\Desktop\Meal Prediction\Weightage Method Code\Weightage For All Flights\Data\Claude\airport_meal_preferences_with_regions_sources.csv"
    mealtime_weights_path = r"C:\Users\9SHRIDA_SUMANTH\OneDrive - Singapore Airlines Limited\Desktop\Meal Prediction\Weightage Method Code\Weightage For All Flights\Data\Claude\meal_time_preferences_with_sources.csv"
    
    print("Done - Read all the inputs! Now passing them to meal system!")

    # Calculate meal distribution
    results = calculate_meal_distribution(
        passenger_df=passenger_data,
        meal_df_path=meal_df_path,
        nationality_weights_path=nationality_weights_path,
        age_weights_path=age_weights_path,
        destination_weights_path=destination_weights_path,
        mealtime_weights_path=mealtime_weights_path
    )
    
    # Save results
    results.to_csv("meal_planning_results.csv", index=False)
    print(f"Processing complete. {len(results)} meal entries generated.")
